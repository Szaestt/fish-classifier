<?php
/**
 * POST /login.php
 * Body (form-data atau JSON): username (boleh isi email), password
 * Return: {ok, user: {id, username, email}}
 */
declare(strict_types=1);
session_start();

header('Content-Type: application/json; charset=utf-8');

function fail(int $code, string $msg): void {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail(405, 'Pakai metode POST.');

$in = $_POST;
if (!$in) {
    $in = json_decode(file_get_contents('php://input'), true) ?? [];
}

$identity = trim((string)($in['username'] ?? $in['email'] ?? ''));
$password = (string)($in['password'] ?? '');

if ($identity === '' || $password === '') {
    fail(400, 'username/email dan password wajib diisi.');
}

$cfg = require __DIR__ . '/../config.php';
require_once __DIR__ . '/../src/Database.php';

try {
    $pdo = Database::pdo($cfg);
    $stmt = $pdo->prepare(
        'SELECT id, username, email, password_hash FROM users
         WHERE username = ? OR email = ? LIMIT 1'
    );
    $stmt->execute([$identity, $identity]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user['password_hash'])) {
        fail(401, 'Username atau password salah.');
    }

    session_regenerate_id(true);
    $_SESSION['user_id']  = (int)$user['id'];
    $_SESSION['username'] = $user['username'];

    echo json_encode([
        'ok' => true,
        'user' => [
            'id' => (int)$user['id'],
            'username' => $user['username'],
            'email' => $user['email'],
        ],
    ], JSON_UNESCAPED_UNICODE);
} catch (PDOException $e) {
    fail(500, 'Database error. Pastikan MySQL nyala & fish_classifier.sql sudah di-import.');
}

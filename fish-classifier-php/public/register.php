<?php
/**
 * POST /register.php
 * Body (form-data atau JSON): username, email, password
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

// Support form-data maupun raw JSON
$in = $_POST;
if (!$in) {
    $in = json_decode(file_get_contents('php://input'), true) ?? [];
}

$username = trim((string)($in['username'] ?? ''));
$email    = trim((string)($in['email'] ?? ''));
$password = (string)($in['password'] ?? '');

if ($username === '' || $email === '' || $password === '') {
    fail(400, 'username, email, dan password wajib diisi.');
}
if (!preg_match('/^[a-zA-Z0-9_.]{3,50}$/', $username)) {
    fail(400, 'Username 3-50 karakter, hanya huruf/angka/underscore/titik.');
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    fail(400, 'Format email tidak valid.');
}
if (strlen($password) < 6) {
    fail(400, 'Password minimal 6 karakter.');
}

$cfg = require __DIR__ . '/../config.php';
require_once __DIR__ . '/../src/Database.php';

try {
    $pdo = Database::pdo($cfg);

    $stmt = $pdo->prepare('SELECT id FROM users WHERE username = ? OR email = ? LIMIT 1');
    $stmt->execute([$username, $email]);
    if ($stmt->fetch()) fail(409, 'Username atau email sudah terdaftar.');

    $stmt = $pdo->prepare('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)');
    $stmt->execute([$username, $email, password_hash($password, PASSWORD_BCRYPT)]);
    $id = (int)$pdo->lastInsertId();

    // Langsung login setelah register
    $_SESSION['user_id']  = $id;
    $_SESSION['username'] = $username;

    echo json_encode([
        'ok' => true,
        'user' => ['id' => $id, 'username' => $username, 'email' => $email],
    ], JSON_UNESCAPED_UNICODE);
} catch (PDOException $e) {
    fail(500, 'Database error. Pastikan MySQL nyala & fish_classifier.sql sudah di-import.');
}

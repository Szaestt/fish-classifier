<?php
/**
 * GET /history.php?limit=20
 * Kalau login: riwayat prediksi milik user itu.
 * Kalau guest: riwayat global terakhir (max 50).
 * Return: {ok, logged_in, username?, count, items[]}
 */
declare(strict_types=1);
session_start();

header('Content-Type: application/json; charset=utf-8');

$cfg = require __DIR__ . '/../config.php';
require_once __DIR__ . '/../src/Database.php';

$limit = max(1, min(50, (int)($_GET['limit'] ?? 20)));
$userId = isset($_SESSION['user_id']) ? (int)$_SESSION['user_id'] : null;

try {
    $pdo = Database::pdo($cfg);

    if ($userId !== null) {
        $stmt = $pdo->prepare(
            'SELECT p.id, p.image_name, p.predicted_class, p.confidence, p.top_k,
                    p.model_name, p.input_size, p.elapsed_ms, p.created_at
             FROM predictions p
             WHERE p.user_id = ?
             ORDER BY p.created_at DESC, p.id DESC
             LIMIT ' . $limit
        );
        $stmt->execute([$userId]);
    } else {
        $stmt = $pdo->query(
            'SELECT p.id, p.image_name, p.predicted_class, p.confidence, p.top_k,
                    p.model_name, p.input_size, p.elapsed_ms, p.created_at,
                    u.username
             FROM predictions p
             LEFT JOIN users u ON u.id = p.user_id
             ORDER BY p.created_at DESC, p.id DESC
             LIMIT ' . $limit
        );
    }

    $items = [];
    foreach ($stmt->fetchAll() as $row) {
        $row['confidence'] = (float)$row['confidence'];
        $row['top_k'] = $row['top_k'] ? json_decode($row['top_k'], true) : null;
        $items[] = $row;
    }

    echo json_encode([
        'ok'        => true,
        'logged_in' => $userId !== null,
        'username'  => $_SESSION['username'] ?? null,
        'count'     => count($items),
        'items'     => $items,
    ], JSON_UNESCAPED_UNICODE);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'ok' => false,
        'error' => 'Database error. Pastikan MySQL nyala & fish_classifier.sql sudah di-import.',
    ], JSON_UNESCAPED_UNICODE);
}

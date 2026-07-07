<?php
/**
 * Konfigurasi terpusat (pengganti src/config.py versi PHP).
 */
return [
    'class_names' => ['Bawal Putih', 'Nila', 'Pari', 'Tongkol', 'Tuna'],
    'num_classes' => 5,
    // Resolusi inference. 224 = paling akurat (~14s), 160 = seimbang (~7s), 128 = cepat (~5s).
    // Model pakai Global Average Pooling jadi fleksibel di ukuran berapapun.
    'img_size'    => 160,
    'top_k'       => 3,
    'model_name'  => 'cnn_scratch',
    'weights_json'=> __DIR__ . '/weights/cnn_scratch.json',
    'weights_bin' => __DIR__ . '/weights/cnn_scratch.bin',
    'max_upload_mb' => 10,

    // ===== DATABASE (XAMPP / phpMyAdmin) =====
    // Import database/fish_classifier.sql dulu di phpMyAdmin.
    // Default XAMPP: user 'root' tanpa password.
    'db' => [
        'host' => '127.0.0.1',
        'port' => 3306,
        'name' => 'fish_classifier',
        'user' => 'root',
        'pass' => '',
    ],
];

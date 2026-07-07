<?php
$cfg = require __DIR__ . '/../config.php';
?>
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐟 Klasifikasi Ikan Indonesia</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">
  <header>
    <h1>🐟 Klasifikasi Ikan Indonesia</h1>
    <p class="sub">CNN inference 100% PHP &mdash; tanpa Python, tanpa server ML eksternal.</p>
    <div class="badges">
      <?php foreach ($cfg['class_names'] as $c): ?>
        <span class="badge"><?= htmlspecialchars($c) ?></span>
      <?php endforeach; ?>
    </div>
  </header>

  <main>
    <div id="drop" class="drop">
      <input type="file" id="file" accept="image/*" hidden>
      <div id="dropInner">
        <div class="drop-icon">📷</div>
        <p><strong>Klik</strong> atau <strong>seret</strong> gambar ikan ke sini</p>
        <small>JPG / PNG / WEBP &middot; maks <?= $cfg['max_upload_mb'] ?> MB</small>
      </div>
      <img id="preview" alt="preview" hidden>
    </div>

    <button id="btn" class="btn" disabled>Prediksi Sekarang</button>

    <div id="status" class="status" hidden></div>

    <div id="result" class="result" hidden>
      <div class="top">
        <div class="top-label">Prediksi</div>
        <div class="top-class" id="topClass">&mdash;</div>
        <div class="top-conf" id="topConf"></div>
      </div>
      <div class="bars" id="bars"></div>
      <div class="meta" id="meta"></div>
    </div>
  </main>

  <footer>
    <p>Model: CNN from scratch &middot; val_acc ~83% &middot; inference <?= $cfg['img_size'] ?>px</p>
  </footer>
</div>
<script src="assets/app.js"></script>
</body>
</html>

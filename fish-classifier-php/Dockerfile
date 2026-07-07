FROM php:8.2-apache

# Install GD (butuh buat baca/resize gambar)
RUN apt-get update && apt-get install -y \
      libpng-dev libjpeg-dev libwebp-dev libfreetype6-dev \
 && docker-php-ext-configure gd --with-jpeg --with-webp --with-freetype \
 && docker-php-ext-install gd \
 && rm -rf /var/lib/apt/lists/*

# PHP limits buat inference yang agak lama
RUN { \
      echo 'max_execution_time=120'; \
      echo 'memory_limit=512M'; \
      echo 'upload_max_filesize=12M'; \
      echo 'post_max_size=14M'; \
    } > /usr/local/etc/php/conf.d/app.ini

# Arahkan docroot Apache ke folder public/
ENV APACHE_DOCUMENT_ROOT=/var/www/html/public
RUN sed -ri 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' \
      /etc/apache2/sites-available/*.conf /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf
RUN a2enmod rewrite

COPY . /var/www/html

# Render/Railway kasih port lewat $PORT; Apache default 80.
COPY docker-entrypoint.sh /usr/local/bin/app-entrypoint
RUN chmod +x /usr/local/bin/app-entrypoint
EXPOSE 80
CMD ["app-entrypoint"]

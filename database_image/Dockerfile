FROM mariadb:10.7.4

# Install wget and unzip for database initialization
RUN apt-get update && \
    apt-get install -y wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy custom entrypoint script
COPY database_image/init-db.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

# Use custom entrypoint that handles DB downloads
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["mysqld"]

# Health check to wait for the database to be ready because database downloads can take time
HEALTHCHECK --interval=30s --timeout=5s --retries=5 --start-period=300s \
    CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1


# Expose the default MariaDB port
EXPOSE 3306

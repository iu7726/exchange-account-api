module.exports = {
  apps: [
    {
      version: '0.1.0',
      name: 'Exchange Account API Server',
      script: './entrypoint_account.sh',
      time: true,
      env: {
        DJANGO_SETTINGS_MODULE: "exchange_account_api.settings",
        PYTHONPATH: "/var/www/og-exchange-api/exchange_account_api",
        PYTHONUNBUFFERED: "TRUE",
      },
    },
  ],
};
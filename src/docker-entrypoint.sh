#!/bin/sh

cat > config.json <<EOF
{
  "telegram_token": "$TELEGRAM_TOKEN",
  "botan_token": "$TELEGRAM_BOTANIO_TOKEN",
  "enabled_modules": [$(for m in $TELEGRAM_BOT_MODULES; do mods=$mods,\"$m\";done; echo $mods | cut -c2-)],
  "image": {"bing_keys": [],
            "google_keys": [{"api_id": "$TELEGRAM_GOOGLE_API_KEY",
                             "cse_id": "$TELEGRAM_GOOGLE_CSE"}],
            "special_groups": []},
  "services_server": "$TELEGRAM_SERVICES_SERVER"
}
EOF

exec "$@"

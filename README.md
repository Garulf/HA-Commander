![GitHub all releases](https://img.shields.io/github/downloads/garulf/ha-commander/total)
# Installation:

### Flow Lancher:

Simply type `pm install ha-commander` to have the plugin installed

### Manual Installation:

Unzip [HA-Commander.zip](https://github.com/Garulf/HA-Commander/releases/latest) to your launchers plugin directory.

| Launcher      | Plugin Path                      |
|---------------|----------------------------------|
| Wox           | `%appdata%\Wox\Plugins`          |
| Flow Launcher | `%appdata%\FlowLauncher\Plugins` |

# Configuration

Please edit your `config.ini` to complete setup:

| Setting    | Type    | Default   | Description                                                                 |
|------------|---------|-----------|-----------------------------------------------------------------------------|
| host       | string  | 127.0.0.1 | Your Home Assistant IP address or hostname                                  |
| port       | int     | 8123      | Your Home Assistant port                                                    |
| token      | string  | None      | https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token |
| ssl        | boolean | true      | Set to true if your Home Assistant uses SSL/HTTPS                           |
| verify_ssl | boolean | true      | Rejects unverified SSL certs if set to true                                 |
| max_items  | int     | 30        | The max results the launcher will display (Lower is faster)                 |

# How-To:

### Basics:

Begin by typing the default ActionWord: "ha"


#### Example:

```ha light```

```ha automation```

HA-Commander will search by `entity_id` and `friendly_name` if set.

### Interaction:

At this time entities can only be toggled.

# Requirements

Python 3.6 or higher

Wox, or Flow Launcher

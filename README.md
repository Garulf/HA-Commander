[![GitHub all releases](https://img.shields.io/github/downloads/garulf/ha-commander/total)](https://github.com/Garulf/HA-Commander/releases/latest)
# Installation:

### Flow Launcher:

![Flow_launcher](https://user-images.githubusercontent.com/535299/145097675-e4d3f41a-4042-4f2a-b707-238b8c6d220c.png)

Simply type `pm install ha-commander` to have the plugin installed

### Manual Installation:

Unzip [HA-Commander.zip](https://github.com/Garulf/HA-Commander/releases/latest) to your launchers plugin directory.

| Launcher      | Plugin Path                      |
|---------------|----------------------------------|
| Wox           | `%appdata%\Wox\Plugins`          |
| Flow Launcher | `%appdata%\FlowLauncher\Plugins` |

# Configuration

NEW in HA-Commander v3.0.0 and up with Flow Launcher 1.9.0 and up:

![147866332-5574f241-9da8-44b8-96eb-8aa526fdeee6](https://user-images.githubusercontent.com/535299/147866412-9f7bb589-b3bd-4ce4-84b0-9f4a5fd0a320.png)




Your settings are now located in your Launcher's settings directory:

| Setting    | Type    | Default          | Description                                                                 |
|------------|---------|------------------|-----------------------------------------------------------------------------|
| host       | string  | http://127.0.0.1 | Your Home Assistant URL                               |
| port       | int     | 8123             | Your Home Assistant port                                                    |
| token      | string  | None             | https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token |
| verify_ssl | boolean | true             | Rejects unverified SSL certs if set to true                                 |
| max_items  | int     | 50               | The max results the launcher will display (Lower is faster)                 |

# How-To:

### Basic:

Begin by typing the default ActionWord: "ha" and an `entity_id` or `friendly_name`

![image](https://user-images.githubusercontent.com/535299/147866294-16f9967a-5e3a-4b26-a4b5-cabd930aaf45.png)


### Advanced:

#### Filter by domains:
Selecting any domain will show all entities from that domain *only*.

![image](https://user-images.githubusercontent.com/535299/147866147-ab6d95c6-566a-4dba-b146-2b6a3e1b62b3.png)


#### Show only light entities:
by typing `ha <domain>.` HA-Commander shows only entities that start with that domain.

![image](https://user-images.githubusercontent.com/535299/147866129-c2da5f73-d48d-471b-ad40-96daa8e1b877.png)


#### Show Logbook:
See recently changed entities by typing `ha @`. Selecting an entry brings up the entity in HA-Commander.

![image](https://user-images.githubusercontent.com/535299/147866210-45d2f0b1-51a1-49ab-9275-dfee143571c0.png)

#### Control light brightness:
Change a lights brightness percentage by typing a number between 0-100 after a light entity

![image](https://user-images.githubusercontent.com/535299/147866261-82521063-8106-4726-8a5a-4f8e0ad6913b.png)

#### Light color and effects:
Light Color & Effects are now in the context menu of supported lights

![image](https://user-images.githubusercontent.com/535299/147866370-eabc81e4-e540-4bff-953d-fb2325fbc9f7.png)

#### Hide entities:
You can now hide entities by invoking the context menu and selecting "Hide Entity"

![image](https://user-images.githubusercontent.com/535299/147866460-f266ecf4-f1dc-4bba-9bae-d636ce17f489.png)


# Requirements

Python 3.8 or higher

Flow Launcher 1.9.0 or higher

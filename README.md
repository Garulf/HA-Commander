# Installation:

Type in Wox:

```wpm install ha-commander```

#### You _MUST_ enter the IP/Password of your Home Assistant server!
Failure to do so will cause the plugin to not work at all.

A cfg file or action word will replace this step soon™

You can do this by opening up main.py in:

```C:\Users\<User>\AppData\Roaming\Wox\Plugins\HA-Commander\```

Edit these lines:

ha_ip = #Home assistant IP

ha_port = #Home assistant port

ha_password = #Your password if any

# How-To:

### Basics:

Begind by typing the default ActionWord: "ha"

This will bring up a list allowing you to filter all entities by service.

You can filter by services listed below:

* group
* automation
* device_tracker
* sensor
* switch
* zone
* sun
* light
* switch
* media_player
* binary_sensor
* device_tracker
* persistent_notification

#### Example:

```ha light```

```ha automation```

Of course just typing will list _ALL_ entities narrowed by your search query.

### Interaction:

Selecting an entity will toggle it by default.

Activating a light entity will toggle it on and off.

While activating a media player will toggle play and pause.

### Advanced:

Typing an entities full "friendly_name" or if no friendly_name, "entity_id" will bring up contextural results according to that entities service. You may also display the entities attributes.

### Planned Features:

* ~Filters~
* ~Basic contextual results~
* Advanced contextual results
* Get Wox context menu to work
* Interact with entity based on modifier key being held (possible with Wox?)

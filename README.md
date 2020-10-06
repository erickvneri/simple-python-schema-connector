# Simple Python ST Schema Connector


This _ST Schema Connector_ project has been designed to deploy two server instances (_**OAuth** and **Webhook Schema Connector**_)
that will interact altogether with the device reference encoded as a JSON Web Token.

In addition, this project has been developed on top of the Python's
[http.server](https://docs.python.org/3/library/http.server.html#module-http.server)
built-in module and uses the [SmartThings Schema Connector Python SDK](https://github.com/erickvneri/st-schema-python)
to integrate virtual devices into the _SmartThings_ platform.

---

## Project scaffolding:

- `run.py` - Module used to call the _OAuth_ and _Webhook_ services.
- `/lib`

    - `/oauth`
        - `data`
            - `user_information` - Module that in charge of user registration and creation of JSON Web Tokens. It will create a `.p` file in reference of the pickle module used to save user information in binary form.
        - `oauth_config`
            - `config` - Module that loads the environment variables from the `.env` file.
        - `public`
            - `login.html`
        - `app.py` - Module that handles Http and provides the OAuth service.

    - `/webhook`
        - `data`
            - `device_information` - Module that get data from the `.p` files that contains the device information.
            - `device_info.p` - File that contains device information for **Discovery Responses**.
            - `device_state_info.p` - File that contains device information for **State Refresh Responses**.
            - `device_info_ref.txt` - Readable reference of the content at the `device_info.p` file.
            - `device_state_info_ref.txt` - Readable reference of the content at the `device_state_info.p` file.
        - `webhook_config` - Module that loads the environment variables from the `.env` file.
        - `my_connector` - Module that handles **Interaction types** with the help of the _SmartThings Schema Connector Python SDK_.
        - `app.py` - Module that handles Http and provides the Webhook service.

---

### Project requirements:
- [Python 3.6](https://www.python.org/downloads/) or greater.
- SmartThings Developer Account.
- SmartThings App (_[developer mode](https://smartthings.developer.samsung.com/docs/testing/developer-mode.html) active_).


### Package installation:

1. Clone this project and install its dependencies:

        git clone git@github.com:erickvneri/simple-python-schema-connector.git
        python3 -m pip install -r requirements.txt

1. To install the _SmartThings Schema Connector Python SDK_ follow [these instructions](https://github.com/erickvneri/st-schema-python#installation).

1. At your working directory, create a `.env` file following the `example.env` file (_you can copy-paste the content of this last one to
ease the process_).


### Deploying services locally:

To deploy both servers, you'll need two separate terminals.

1. To deploy the OAuth server, run the following command at your first terminal:

        python3 run.py --service oauth

1. To deploy the Webhook Schema Connector server, run the following command at your first terminal:

        python3 run.py --service webhook


### Enable tunneling services:

To expose both apps at the World Wide Web, I recommend you to use [localtunnel](https://www.npmjs.com/package/localtunnel) as it allows to deploy multiple tunneling instances with no payment needed.

As we did in the last step, you'll need two separate terminals to deploy both _localtunnel_ instances.

1. Enable tunneling service for OAuth server at your third terminal:

        lt --port 5000 --print-requests

1. Enable tunneling service for Webhook server at your fourth terminal:

        lt --port 8000 --print-requests

### Create your ST Schema Connector project:

1. Access your [Developer Workspace](https://smartthings.developer.samsung.com/workspace).
1. Create your project following this sequence of steps:

    - _New Project_ -> _Device Integration_ -> _SmartThings Cloud Connector_ -> _SmartThings Schema Connector_ -> _Name your app_.

1. Click at **Register App**.
1. Select **Webhook Endpoint** and copy-paste the localtunnel url (**_port 8000_**) and include the `/my-schema-connector` endpoint as follows:

        https://example-webhook-url.loca.lt/my-schema-connector

1. Click **Next** to register your OAuth configuration. If you're using the dummy credentials from the `example.env` file,
use the following values:
    - **Client Id**: dummy-client-id
    - **Client Secret**: dummy-client-secret

1. As OAuth endpoints, copy-paste the localtunnel url (**_port 5000_**) and include the `/authorize` and `/token` endpoints as follows:
    - **Authorization URI**: https://example-oauth-url.loca.lt/authorize
    - **Token URI**: https://example-oauth-url.loca.lt/token
1. (_Optional_) Fill the _Scopes_ field and click **Next**.
1. Fill the **App Display Name** field.
1. To finalize, upload a **240x240 .png** image and click **Save**.


### Deploy your project at the SmartThings App:

1. From the _Dashboard_, tap the **"+"** sign and select **"Device"**.
1. At the bottom of the **"By device type"** section, select **"My Testing Devices"**.
1. Track your project and select it.
1. Once the **Login page** has been deployed, you'll be able to select a few example devices for demonstration.
1. Finalize the installation and test the example devices. By default, the _Webhook server_ has enabled the logger instance from the
_SmartThings Schema Connector Python SDK_, therefore, you'll get full detail of the interaction types received at your terminal.

---
To learn more about _SmartThings Schema Connector_ integrations, please visit our _[main documentation](https://smartthings.developer.samsung.com/docs/devices/smartthings-schema/schema-basics.html)_
or share your questions at our _[Community Forums](https://community.smartthings.com/c/developer-programs)_.
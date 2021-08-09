# ULHacks Bot

A Discord bot for the ULHacks Discord server.

## Setup

Clone the repository using [Git](https://git-scm.com/downloads) and enter it using the commands below:

```sh
git clone https://github.com/GeeTransit/ulhacks-bot
cd ulhacks-bot
```

Install [Python](https://www.python.org/downloads/) (minimum is 3.9) and create the virtual environment by running:

```sh
# On Windows
python -m venv .venv
# On Linux
python3 -m venv .venv
```

To enter the virtual environment, run the following. To leave the virtual environment, type `deactivate` and press enter.

```sh
# On Windows
call .venv\Scripts\activate.bat
# On Linux
source .venv/bin/activate
```

Install all dependencies by entering the virtual environment and running:

```sh
# On Windows
pip install -r requirements.txt
# On Linux
pip3 install -r requirements.txt
```

## Config

The ULHacks bot takes all configuration using environment variables. Here's a table with the environment variables needed:

| Name              | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| ULHACKS_BOT_TOKEN | Discord bot user's token. Should be around 59 characters long and look random. |
| ULHACKS_ENV       | Environment the bot is running in. Defaults to `local`.      |

You can get your Discord bot user's token by going to [your dashboard](https://discord.com/developers/applications), clicking on your application, clicking *Bot* in the left sidebar, and pressing the *Copy* button under *Token* in the *Build-A-Bot* section.

If you don't have an application, click *New Application* on the top right and choose a name (you can change it later).

If you don't have a bot user, press *Add Bot* in the *Build-a-Bot* section and click *Yes, do it!*

To set an environment variable, run:

```sh
# On Windows
set NAME=value
# On Linux
export NAME=value
```

## Usage

Enter the virtual environment and run:

```sh
# On Windows
python ulhacks_bot.py
# On Linux
python3 ulhacks_bot.py
```

## More Config

### Running Locally

If the ULHACKS_ENV environment variable is not set or is set to `local`, the bot will use a local data store.

| Name                        | Purpose                                                      |
| --------------------------- | ------------------------------------------------------------ |
| ULHACKS_JSON_STORE_FILENAME | The filename the JSON store uses. Defaults to `json-store.json`. |

### Running on Heroku

If the ULHACKS_ENV environment variable is set to `heroku`, the bot will use a PostgreSQL data store.

| Name         | Purpose                                                      |
| ------------ | ------------------------------------------------------------ |
| DATABASE_URL | The URI the PostgreSQL store uses. Should start with `postgres://`. |


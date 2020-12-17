import os
# Use the package we installed
import logging
import random
import json

from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient
from zipfile import ZipFile

logging.basicConfig(level=logging.DEBUG)


# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.event("app_mention")
def event_test(body, say, logger, client):
    logger.info(body)
    # say(f"Hello there you <@{body['event']['user']}> :smile:!")

    client.chat_postEphemeral(channel=body['event']['channel'], user=body['event']['user'],
                              text=f"Hello there you <@{body['event']['user']}> :smile:!")


@app.command("/backup_channel")
def command_backup(ack, body, command, logger, client):
    ack()
    logger.info(command)

    result = client.users_list()
    users = save_users(result['members'])

    wClient = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    response = wClient.conversations_history(channel=command['channel_id'])

    file1 = open("CondensedMessages.txt", 'w+')

    for message in response["messages"]:
        file1.write(users[message["user"]]['name'] + " " + message["text"] + '\n')
        # file1.write(users[message["user"]] + " " + message["text"] + '\n')

    file1.close()
    file2 = open("completeText.txt", 'w+')
    file2.write(str(response["messages"]))
    file2.close()
    # The name of the file you're going to upload
    file_name = "./backup.zip"
    # ID of channel that you want to upload file to
    channel_id = command['channel_id']
    zipObj = ZipFile('backup.zip', 'w')
    zipObj.write('CondensedMessages.txt')
    zipObj.write('completeText.txt')
    zipObj.close()

    try:
        # Call the files.upload method using the WebClient
        # Uploading files requires the `files:write` scope
        result = client.files_upload(
            channels=channel_id,
            initial_comment="Here's a back up of the channel's conversations:smile:",
            file=file_name,
        )
        # Log the result
        logger.info(result)

    except SlackApiError as e:
        logger.error("Error uploading file: {}".format(e))


def save_users(users_array):
    users_store = {}
    for user in users_array:
        # Key user info on their unique user ID
        user_id = user["id"]
        # Store the entire user object (you may not need all of the info)
        users_store[user_id] = user
    return users_store


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

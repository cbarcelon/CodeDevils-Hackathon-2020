import os
# Use the package we installed
import logging
import random
import json

from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient
from zipfile import ZipFile

logging.basicConfig(level=logging.DEBUG)

tips = [
    "Always make sure that you update the Request URL when restarting ngrok",
    "Make sure you check your scopes when an API method does not work",
    "Every API call has a scope check that you use the correct ones and when calling something new add that scope on Slack",
    "After changing the scope you need to install your App again",
    "Every Event you want to use, you need to subscribe to on Slack",
    "Every Slack command needs the Request URL",
    "The Bot token is on the Basics Page",
    "The Slack Signing Secret is on the OAuth & Permission page",
    "Limit the scopes to what you really need",
    "You can add collaborators to your Slack App under Collaborators, they need to be in the workspace",
    "To use buttons you need to enable Interactive Components",
    "Always go in tiny steps, use the logger or print statements to see where you are and if events reach your app",
    "If the user does something on Slack always send a response, even if it is just an emoji",
    "Your App can use on the users behalf, you need to get User Scopes in that case. Later this would lead to having to save user tokes",
    "Do not plan to much, do simple things first, when you get these done then start to dream big",
    "Storing persistent data in a DB makes sense, when you are not familiar with it maybe a dict in a file might be enough for now",
    "Oauth -- so authenticating the app and user is important when distributing your app, while locally developing it is not that important yet, get some functionality going first",
    "Have the Slack API, Slack Events and your Slack Build App page open in your browser to have fast access",
    "Slash commands need to be unique in a workspace, so do append your bots name to them"
]

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


@app.command("/py_tips")
def command_tip(ack, body, command, logger, client):
    ack()
    logger.info("YIPPIEKAYAKOTHERBUCKETS")
    logger.info(command)
    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":smile: You asked for a tip, here you go"
            }
        }
    ]
    attach = [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{random.choice(tips)}"
                    }
                }
            ]
        }
    ]
    client.chat_postMessage(channel=command['channel_id'], blocks=block, attachments=attach)


@app.command("/backup_channel")
def command_backup(ack, body, command, logger, client):
    ack()
    logger.info("YIPPIEKAYAKOTHERBUCKETS")
    # logger.info(command)
    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":smile: You asked for a backup, here you go"
            }
        }
    ]
    attach = [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Backup started"
                    }
                }
            ]
        }
    ]
    # client.chat_postMessage(channel=command['channel_id'], blocks=block, attachments=attach)

    wClient = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    response = wClient.conversations_history(channel=command['channel_id'])
    # logger.info(wClient.conversations_history(channel=command['channel_id']))
    # saveConversation(wClient.conversations_history(channel=command['channel_id'], logger=logger))
    file1 = open("CondensedMessages.txt", 'w+')

    default = " "
    for message in response["messages"]:
        file1.write(message["user"] + " " + message["text"] + '\n')


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



# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

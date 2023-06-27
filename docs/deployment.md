# Deployment Guide

This will be a relatively loose guide of AWS Lambda deployment; it should be enough to give you the major steps, but it won't deal with every issue that will probably pop up. Also, this will be a high-noise, low-signal document, with the intention of just documenting *everything* that I think may be useful. Once I understand this better, we can work on parsing it down.

## Big Idea

- Use AWS Lambda for the server, since we expect low traffic. As traffic increases, if needed, we transfer to EC2. Pricing for labmda is [forgiving](https://aws.amazon.com/lambda/pricing/)
- Use Flask for the backend. Lightweight and customizable, also there were many guides for running flask on Lambda.
- Use (something) for frontend (React? Next.js?)? Not there yet but it's something to do soon. Want it to be as plug-and-play as possible.
- Use [Zappa](https://github.com/zappa/Zappa) to deploy. Very easy, I am very impressed with this. I think that you need your [AWS CLI](https://aws.amazon.com/cli/) configured so Zappa can actually interact with AWS. Also, Zappa docs are very good.

## During Dev

Always develop in the virtual environment! Zappa uses `requirements.txt` to install dependencies into a binary on S3 which is then imported into the Lambda instance. Therefore we want the minimum required number of packages in `requirements.txt` to keep the S3 weight low and the transfer times minimal. Dumping your normal `pip3 freeze` into `requirements.txt` will make everything costly and slow. Several times during development, my virtual environment's installed packages were polluted with my normal installed packages, which promped me to delete the virtual environment and start again.

## Initial Deployment

Run `zappa init` and follow along. Be in the virtual environment when you `zappa init`, because I think that it looks at installed packages to guess whether you are using `flask` or `django`, and it thought that FTB was using django a couple times. Being in the virtualenv fixed that.

Another thing to note: Zappa needs the file and variable name of the `Flask()` object, which is `application.application` (since our entry point is `application.py`, and the Flask app is defined as `application = Flask(__name__)`. It is good at finding it, and you will have to approve it's guess of `application.application` during `zappa init`.

Integrating the backend `pythonToolbox` will be necessary to access the DB stuff. So there are two options:
- Plop ftb code into `pythonToolbox` and deploy within there
- Refactor the DB code out into `ftb` and import DB code into `pythonToolbox` from `ftb` as needed

I think that the second option would be cleaner: it'd be easier to deal with dependencies and `requirements.txt` and give us a good opportunity to refactor the DB code. But it's up to you!

You'll name the deployment, too - I suggest `dev` for development, `prod` for production, etc. Start w/ `dev` untill it's ready.

## Deployment and Updating

`zappa deploy dev` to deploy it (initialize the lambda instances and the s3 bucket)

`zappa update dev` to update it (update the lambda instances w/ your new code)

`zappa undeploy dev` to undeploy it (woa!)

## TODO

- How to link the deployment with a domain name?
- How to link private keys? I skimmed this [this](https://stackoverflow.com/questions/64940495/zappa-where-to-put-aws-secret-access-keys),may be useful. A good Nitu question.

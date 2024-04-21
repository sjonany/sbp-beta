# SBP beta organizer
A low-effort organizer of instagram beta videos for seattle bouldering project.
See the resulting sheet [here](https://docs.google.com/spreadsheets/d/1Lzv5nxedHZdkPOKd-pLdd_F7D45q-nl6wKUn9gwEtsw/edit#gid=606245102).

![Stephen Jonany's Video - Apr 20, 2024](https://github.com/sjonany/sbp-beta/assets/1094318/5a81b6c2-3f8c-4aae-ad45-383252f7fe6b)


## Usage
- To run the script, run `poetry run python runner.py` on a commandline.

## Setup
- Create google sheets token [here](https://console.cloud.google.com/apis/api/sheets.googleapis.com/metrics?project=<project-name>).
	- Create credentials > Oauth client id > desktop app
	- Use this scope: https://www.googleapis.com/auth/drive.file
	- Save the generated file in `secret/sheets_secret.json`
	- Other references
		- https://stackoverflow.com/questions/75454425/access-blocked-project-has-not-completed-the-google-verification-process
		- https://developers.google.com/sheets/api/quickstart/python
- You also need to create a textfile `secret/insta_password.txt`. See `insta.py` for the login name. It's currently hardcoded.

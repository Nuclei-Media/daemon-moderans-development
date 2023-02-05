# Nuclei

built using Fastapi and flutter and respective extensions.

Nuclei is a web application that allows you to upload and manage your own compressed media to increase media availability and accessibility.

<h2> instructions on running server</h2>

- run these commands in your terminal _having admin privs helps_
- ```
  # only works for me so if you're me run: python docker_refresher.py
  cd prod && docker-compose up
  python main.py
  ```

  This is meant to run on windows, i daf about your linux supremacy, this will run on windows for now.

- prod docker-compose file will build the project whereas dev docker will pull a correct version of backend

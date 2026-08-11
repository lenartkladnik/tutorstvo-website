# Tutorstvo website

## Working examples:
- [tutorstvo.sentvid.org (Gimnazija Šentvid)](https://tutorstvo.sentvid.org)

## Running

### Prerequisites
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/)

```bash
# Clone the project
cd ~
git clone https://github.com/lenartkladnik/tutorstvo-website
cd tutorstvo-website


# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


# Run app
# First add necessary fields in .secrets (you can refer to .secrets-template)

# Manually running
python app.py

# (RECOMMENDED) Create a systemd service (don't forget to change the path to compose.yaml)
echo "[Unit]
Description=Tutorstvo app service

[Service]
ExecStart=docker compose -f /path/to/compose.yaml up --build
Restart=never

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/tutorstvo-website.service
systemctl daemon-reload
systemctl enable --now tutorstvo-website.service
```

## Updating
```bash
cd ~/tutorstvo-website
git pull origin main
# If you made a service also restart that
systemctl restart tutorstvo-website.service
```

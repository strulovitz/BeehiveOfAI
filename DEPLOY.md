# Deploy Your Own BeehiveOfAI

**Get your distributed AI marketplace live on the internet — in about 15 minutes.**

---

## Step 0: What You Need

- A computer with Python 3.10+ installed
- The BeehiveOfAI code (clone from GitHub)
- A domain name (optional for testing, required for production)

That's it. No cloud account. No credit card. No DevOps experience.

---

## Step 1: Get the Code Running Locally

```bash
git clone https://github.com/strulovitz/BeehiveOfAI.git
cd BeehiveOfAI
pip install -r requirements.txt
python seed_data.py
python app.py
```

Open http://localhost:5000 — you should see the BeehiveOfAI homepage.

Test accounts (password `test123` for all):
- Worker Bee: worker1@test.com
- Queen Bee: queen1@test.com
- Beekeeper: company1@test.com

Explore the dashboard, submit a job, check the balance page. Everything works in free test mode.

---

## Step 2: Choose Your Hosting

You have three options, from free to bulletproof:

### Option A: Your Own Computer + Cloudflare Tunnel (Free)

**Cost:** $0/month + ~$10/year for a domain

**Best for:** Getting started, first users, MVP testing.

This is how beehiveofai.com itself runs. Your computer acts as the server, and Cloudflare Tunnel creates a secure connection from the internet to your machine — no port forwarding, no static IP needed.

**Steps:**

1. **Get a domain** — Buy one at [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/) (~$10/year, cheapest option). Or use any registrar and point your nameservers to Cloudflare.

2. **Install Cloudflare Tunnel:**
   - Create a free [Cloudflare account](https://www.cloudflare.com/)
   - Add your domain to Cloudflare
   - Install `cloudflared`: download from [Cloudflare's GitHub releases](https://github.com/cloudflare/cloudflared/releases)
   - Authenticate: `cloudflared tunnel login`
   - Create tunnel: `cloudflared tunnel create mybeehive`
   - Route DNS: `cloudflared tunnel route dns mybeehive yourdomain.com`

3. **Create tunnel config** (`~/.cloudflared/config.yml`):
   ```yaml
   tunnel: YOUR_TUNNEL_ID
   credentials-file: /path/to/.cloudflared/YOUR_TUNNEL_ID.json
   ingress:
     - hostname: yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```

4. **Set your secret key and start:**
   ```bash
   # Windows:
   set BEEHIVE_SECRET_KEY=any-long-random-string-here
   python run_production.py

   # Linux/Mac:
   export BEEHIVE_SECRET_KEY=any-long-random-string-here
   python run_production.py
   ```

5. **Start the tunnel** (in a separate terminal):
   ```bash
   cloudflared tunnel run mybeehive
   ```

6. Visit `https://yourdomain.com` — your site is live, with free SSL from Cloudflare.

**Keep in mind:** Your computer must stay on for the site to work. Power outage or reboot = site goes down. This is fine for getting started, but you'll want a VPS eventually.

---

### Option B: A Cheap VPS ($4-5/month)

**Cost:** ~$4-5/month + ~$10/year for a domain

**Best for:** Reliable 24/7 uptime, real users, a proper deployment.

**Recommended VPS providers:**

| Provider | Cheapest Plan | Notes |
|----------|--------------|-------|
| [Hetzner](https://www.hetzner.com/cloud/) | ~$4.15/mo | Best price-to-value. Servers in Germany, Finland, US. |
| [DigitalOcean](https://www.digitalocean.com/) | $4/mo | Great tutorials. Beginner-friendly. |
| [Vultr](https://www.vultr.com/) | $6/mo | 30+ locations worldwide. |
| [Linode](https://www.linode.com/) | $5/mo | Solid, reliable, good support. |

**Steps (Ubuntu VPS):**

1. **Create a VPS** — Choose Ubuntu 22.04 or 24.04 LTS, smallest plan.

2. **SSH in and set up:**
   ```bash
   # Connect to your server
   ssh root@YOUR_SERVER_IP

   # Create a non-root user
   adduser beehive
   usermod -aG sudo beehive

   # Set up firewall
   ufw allow 22
   ufw allow 80
   ufw allow 443
   ufw enable

   # Switch to the new user
   su - beehive
   ```

3. **Install dependencies and deploy:**
   ```bash
   sudo apt update && sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git -y

   git clone https://github.com/strulovitz/BeehiveOfAI.git
   cd BeehiveOfAI
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python seed_data.py
   ```

4. **Create a systemd service** (`/etc/systemd/system/beehive.service`):
   ```ini
   [Unit]
   Description=BeehiveOfAI
   After=network.target

   [Service]
   User=beehive
   WorkingDirectory=/home/beehive/BeehiveOfAI
   Environment=BEEHIVE_SECRET_KEY=your-long-random-secret-here
   ExecStart=/home/beehive/BeehiveOfAI/venv/bin/python run_production.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable beehive
   sudo systemctl start beehive
   ```

5. **Set up Nginx** (`/etc/nginx/sites-available/beehive`):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/beehive /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Point your domain** — In your domain registrar, set the A record to your VPS IP address.

7. **Add SSL:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

Done. Your site runs 24/7, survives reboots, and has SSL.

---

### Option C: Platform-as-a-Service (Render, Railway, Fly.io)

**Cost:** $0-7/month

**Best for:** Developers who want zero server management.

**Important:** These platforms use ephemeral filesystems — SQLite data won't survive deploys. You'll need to switch to PostgreSQL (change one line in the config).

| Platform | Free Tier? | Notes |
|----------|-----------|-------|
| [Render](https://render.com/) | Yes (apps sleep after 15 min idle) | Easiest setup. Connect GitHub, deploy. |
| [Railway](https://railway.app/) | Trial credits only | Clean UI. ~$5-7/mo for a small app. |
| [Fly.io](https://fly.io/) | Small free allowance | Supports persistent SQLite via volumes. More technical. |

For Render: connect your GitHub repo, set `BEEHIVE_SECRET_KEY` in environment variables, add a `render.yaml` or let it auto-detect Python. Add a PostgreSQL database ($7/mo).

---

## Step 3: Connect Payments

See [PAYMENT_GUIDE.md](PAYMENT_GUIDE.md) for detailed instructions on connecting YOUR payment provider.

Short version: the platform works fully in free test mode. When you're ready for real money, use an AI coding assistant to wire up Stripe, PayPal, or whatever works in your country.

---

## Step 4: Connect Worker/Queen Computers

BeehiveOfAI is the website — the "Hub." To actually process AI tasks, you need computers running the client software:

**[HoneycombOfAI](https://github.com/strulovitz/HoneycombOfAI)** — the Worker/Queen Bee client.

On each Worker/Queen computer:
```bash
git clone https://github.com/strulovitz/HoneycombOfAI.git
cd HoneycombOfAI
pip install -r requirements.txt
# Edit config.yaml: set server URL to YOUR domain, set mode (worker/queen)
python honeycomb.py
```

Workers poll your website for tasks, process them locally using Ollama (or other AI backends), and submit results back. The Queen coordinates the work.

---

## Step 5: Customize for Your Market

Things you might want to change:

| Setting | Where | Default |
|---------|-------|---------|
| Nectar package prices | `app.py` → `NECTAR_PACKAGES` | $18 / $40 / $75 |
| Revenue split | `app.py` → `PLATFORM_FEE_PERCENT` etc. | 5% / 30% / 65% |
| Harvest threshold | `app.py` → `HARVEST_THRESHOLD` | $50 |
| Site name/branding | `templates/base.html` | BeehiveOfAI |
| Domain | Cloudflare / DNS settings | yourdomain.com |

---

## Database Note

BeehiveOfAI uses **SQLite** by default — a simple file-based database. This is perfect for small deployments (up to ~100 concurrent users). If you need more:

- Switch to PostgreSQL: change the `SQLALCHEMY_DATABASE_URI` in `app.py`
- Flask-SQLAlchemy makes this a one-line change
- Required if using Render or Railway (no persistent filesystem)

---

## Production Checklist

Before going live with real users and real money:

- [ ] Set a strong `BEEHIVE_SECRET_KEY` (long random string)
- [ ] Enable HTTPS (Cloudflare, Certbot, or PaaS handles this)
- [ ] Connect a payment provider (see PAYMENT_GUIDE.md)
- [ ] Change default test account passwords or delete them
- [ ] Set up database backups (for SQLite: just copy the `.db` file daily)
- [ ] Test the full flow: register → buy nectars → submit job → process → receive result

---

## Questions?

Read the full story behind this project in [The Distributed AI Revolution](https://github.com/strulovitz/TheDistributedAIRevolution) — a free book that covers everything from the architecture to the business model to the payment infrastructure.

# Nuclei Templates Collector

This repository contains a tool to manage, organize, and categorize Nuclei templates for penetration testing. It automates cloning multiple template repositories, removing duplicates, and organizing them by category for easy usage.

---

## Features

- Clone or update multiple Nuclei template repositories.
- Automatically skip private or inaccessible repositories (404 / authentication required).
- Scan and remove duplicate templates.
- Organize templates into categories.
- Display detailed categorization summary with counts and percentages.
- Supports large-scale template management (hundreds of thousands of templates).

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yezeiyashein/nuclei-tc.git
cd nuclei-tc
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

> Requirements include:
> - Python 3.10+
> - rich
> - PyYAML

---

## Usage

1. Prepare your repositories list in `repos.txt` (one GitHub repo URL per line).
2. Prepare your category mapping in `categories.json`.
3. Run the manager:

```bash
python nuclei-tc.py
```

The script will:

- Clone or update repositories.
- Scan templates.
- Remove duplicates.
- Organize templates into categories.
- Display a summary of templates per category.

---

## Template Categories and Impact

| Category              | Description                                           | Typical Impact                                                                 |
|-----------------------|-------------------------------------------------------|-------------------------------------------------------------------------------|
| wordpress             | Templates targeting WordPress CMS                     | Exploits misconfigurations, outdated plugins/themes, weak authentication      |
| xss                   | Cross-Site Scripting vulnerabilities                 | Steal cookies, session tokens, or perform malicious scripts in victim browsers|
| rce                   | Remote Code Execution                                | Execute arbitrary code on the target server                                   |
| sql_injection         | SQL Injection                                        | Access, modify, or exfiltrate database content                                 |
| subdomain_takeover    | Subdomain takeover                                   | Attacker can claim unused subdomains to host malicious content                 |
| cve                   | CVE-based vulnerabilities                             | Exploits known CVEs to compromise systems                                      |
| http                  | HTTP misconfigurations                                | Information disclosure, unauthorized access                                   |
| exposed               | Exposed services, files, or endpoints               | Data leaks, credential exposure                                              |
| auth                  | Authentication bypass                                 | Gain unauthorized access to accounts or services                              |
| joomla                | Joomla CMS-specific vulnerabilities                  | Exploit outdated components or misconfigurations                               |
| apache                | Apache server misconfigurations                       | Information disclosure or RCE                                                  |
| lfi                   | Local File Inclusion                                  | Read sensitive files from the server                                          |
| drupal                | Drupal CMS-specific vulnerabilities                  | Exploit known vulnerabilities to compromise Drupal sites                      |
| aws                   | AWS misconfigurations or exposed services           | Unauthorized access to cloud resources                                         |
| php                   | PHP-based vulnerabilities                             | Code execution, information disclosure                                        |
| api                   | API-specific vulnerabilities                           | Unauthorized access or data leakage                                           |
| docker                | Docker misconfigurations                              | Container breakout, sensitive data exposure                                   |
| postgres              | PostgreSQL misconfigurations                          | Database compromise                                                           |
| open_redirect         | Open redirect vulnerabilities                          | Phishing or redirect attacks                                                  |
| debug                 | Debug endpoints exposed                                | Information disclosure                                                        |
| jenkins               | Jenkins misconfigurations or exposed endpoints       | CI/CD compromise, code execution                                              |
| ssrf                  | Server-Side Request Forgery                             | Internal network scanning or data exfiltration                                 |
| magento               | Magento CMS-specific vulnerabilities                  | Exploit outdated components or misconfigurations                               |
| nodejs                | NodeJS application vulnerabilities                     | RCE, file inclusion, or sensitive data exposure                                |
| backup                | Exposed backup files                                   | Data exfiltration                                                             |
| nginx                 | Nginx misconfigurations                                 | Information disclosure, HTTP header manipulation                               |
| fuzz                  | Fuzzing templates                                      | Find unexpected endpoints or vulnerabilities                                   |
| git                   | Exposed `.git` repositories                             | Source code leakage, sensitive data exposure                                  |
| graphql               | GraphQL endpoint vulnerabilities                         | Data leakage, unauthorized access                                             |
| mysql                 | MySQL misconfigurations                                  | Database compromise                                                           |
| exposed_tokens        | Exposed API keys, credentials                           | Unauthorized access or account takeover                                       |
| xxe                   | XML External Entity vulnerabilities                       | Data exfiltration, SSRF, or DoS attacks                                       |
| template_injection    | Server-side template injection                             | Code execution or data leakage                                                |
| crlf_injection        | CRLF injection                                           | HTTP header injection, cache poisoning                                         |
| directory_listing     | Directory listing misconfigurations                     | Sensitive files exposure                                                      |
| rfi                   | Remote File Inclusion                                     | Code execution                                                               |
| csrf                  | Cross-Site Request Forgery                                 | Unauthorized actions on behalf of users                                       |
| cms                   | Generic CMS vulnerabilities                               | Exploit CMS misconfigurations or weak setups                                   |

> ⚠️ **Note:** This table helps prioritize vulnerabilities during pentests. Some categories may overlap depending on the templates used.

---

## Example Output

```
[*] Starting clone/update for 3 repos
[!] Skipped private or inaccessible repo: example/repo (404 Not Found)
[*] Scanning templates and counting duplicates...
[✓] Scanned 800331 templates, removed 538447 duplicates.
[*] Organizing templates and categorizing...
[*] Cleaning up cloned repo folders...

Template Categorization Summary
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┓
┃ Category           ┃  Count ┃ Percent ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━┩
│ wordpress          │ 199373 │   76.1% │
│ other              │  31439 │   12.0% │
│ subdomain_takeover │    524 │    0.2% │
└────────────────────┴────────┴─────────┘
TOTAL: 261884
```

---

## Usage for Pentesting

- Use specific category folders like `subdomain_takeover` or `rce` to target relevant vulnerabilities.
- Run Nuclei scans against your target domains:

```bash
nuclei -t community-templates/subdomain_takeover -u https://target.com
```

- Vulnerable findings are displayed per template with relevant metadata.
- Example impact: Subdomain takeover can allow attackers to host malicious content, intercept traffic, or phish credentials.

---

## License

MIT License


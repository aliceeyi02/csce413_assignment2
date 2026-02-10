# Honeypot Analysis

## Summary of Observed Attacks

The honeypot successfully acted as a "security sensor," capturing a variety of simulated adversarial actions. Because the decoy was positioned on a non-standard port (5002), any traffic reaching it was immediately classified as suspicious.

- The system logged multiple HTTP POST requests containing cleartext usernames and passwords

- The logs captured several SQL injection strings (such as ' OR 1=1 --) aimed at discovering sensitive database information

- The system identified rapid fire reconnaissance from automated scripts attempting to banner grab and identify the underlying web framework

## Notable Patterns

- I observed burst patterns where dozens of login attempts occurred within a single second. This high velocity is a definitive indicator of brute force automation rather than manual human entry

- By analyzing the user agent strings, I identified that the majority of the attacks were initiated from python curl requests, indicating that the attacker was likely using custom scripts rather than a standard web browser

## Recommendations

To maximize the value of the honeypot data, I recommend integrating logs with a tool like Fail2Ban to immediately blacklist any IP that interacts with the decoy. Furthermore, the administration could try fake credentials that provide definitive proof of a successful breach. Having this hook up with some sort of alerting system would transform the honeypot into a proactive detection service, providing the security team with an immediate signal before an attacker can pivot to legitimate services.
 # Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you believe you have found a security vulnerability in Zenith Analyser, please report it to us through coordinated disclosure.

**Please do NOT report security vulnerabilities via GitHub issues, discussions, or pull requests.**

### How to Report

1. **Email**: Send an email to security@example.com
2. **Encryption**: Use our PGP key (available upon request)
3. **Details**: Include as much information as possible:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: Our security team will assess the vulnerability
- **Updates**: We will provide regular updates on our progress
- **Fix**: We will work on a fix and coordinate disclosure
- **Credit**: We will credit you in the security advisory (if desired)

### Disclosure Policy

We follow a 90-day disclosure deadline. We will:
1. Notify you when the report is received
2. Confirm the vulnerability and begin working on a fix
3. Notify you when the fix is deployed
4. Publish a security advisory after 90 days or when a fix is available

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of Zenith Analyser
2. **Validate Input**: Validate all input before processing
3. **Use Sandboxing**: Run untrusted code in isolated environments
4. **Monitor Dependencies**: Keep all dependencies up to date
5. **Follow Least Privilege**: Run with minimal necessary permissions

### For Developers

1. **Input Validation**: Always validate and sanitize input
2. **Type Safety**: Use type hints and static analysis
3. **Testing**: Write security-focused tests
4. **Dependencies**: Monitor and update dependencies regularly
5. **Code Review**: Perform security-focused code reviews

## Known Security Considerations

### Lexer/Parser
- The lexer and parser handle arbitrary input
- Ensure proper input validation when using with untrusted sources
- Consider resource limits for very large inputs

### Time Calculations
- Time conversion functions handle arithmetic operations
- Ensure proper bounds checking to prevent overflow

### AST Processing
- AST manipulation can be memory intensive
- Set appropriate limits for deep nesting

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2). Critical security fixes may be backported to previous major versions.

## Responsible Disclosure Guidelines

We appreciate security researchers following these guidelines:

1. **Do no harm**: Do not attempt to disrupt services or damage data
2. **Privacy**: Respect the privacy of others
3. **Lawfulness**: Act within applicable laws and regulations
4. **Coordination**: Allow us time to fix the issue before public disclosure
5. **Good faith**: Act in good faith to improve security

## Security Contacts

- Primary: frasasudev@gmail.com
- Backup: frasasudev@gmail.com

## Security-Related Configuration

When deploying Zenith Analyser in production:

1. Set appropriate resource limits
2. Use isolated execution environments
3. Monitor for anomalous behavior
4. Keep logs of all operations
5. Regular security audits

## Third-Party Dependencies

We regularly audit our dependencies for security vulnerabilities. See `pyproject.toml` for the complete list.

## Bug Bounty

We currently do not have a formal bug bounty program. However, we appreciate and acknowledge security researchers who responsibly disclose vulnerabilities.

## License

This security policy is part of the Zenith Analyser project and is covered by the Apache 2.0 license.

# Contributing to zephyr-vexriscv

Thank you for your interest in contributing! This document provides guidelines to help us maintain a high-quality project and ensure a smooth contribution process.

## Development Environment

### Prerequisites
- Python 3.8 or later
- RISC-V toolchain
- Zephyr SDK
- LiteX (for FPGA development)
- FPGA toolchain for your target board (Gowin, etc.)

### Setup
```bash
# Clone the repository
git clone https://github.com/SantaCRC/zephyr-vexriscv.git
cd zephyr-vexriscv

# Install Python dependencies
pip install -r requirements.txt

# Initialize submodules (if applicable)
git submodule update --init --recursive
```

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**, following our code style guidelines.

3. **Test your changes** thoroughly:
   - For software changes, run relevant tests
   - For hardware changes, test on actual hardware when possible
   - Ensure your changes don't break existing functionality

4. **Commit your changes** with clear, descriptive commit messages:
   - Use the imperative mood ("Add feature" not "Added feature")
   - Reference issues if applicable ("Fixes #123")
   - Keep first line under 50 characters
   - Provide detailed description in the body if necessary

5. **Push to your fork** and submit a pull request.
   - Clearly describe what your changes do and why they should be included
   - Include the relevant issue number if applicable

6. **Address review feedback** until your contribution is accepted.

## Code Style

### Python Code
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Use meaningful variable and function names
- Include docstrings for functions and classes

### C/C++ Code
- Follow the existing style in the codebase
- Use 4-space indentation
- Always initialize variables
- Comment complex logic

### Hardware Description Code
- Document interfaces clearly
- Follow LiteX conventions for signal naming

## Common Project Decisions

When contributing, be aware of these common guidelines:

- New board support requires maintainer capacity
- Prefer standard interfaces over custom solutions
- SoC design changes require thorough discussion
- Maintain compatibility with upstream Zephyr when possible

## Reporting Issues

- Use [GitHub Issues](../../issues) to report bugs or request features.
- Include detailed steps to reproduce bugs.
- For hardware issues, specify:
  - Board type and revision
  - FPGA toolchain version
  - Relevant hardware configuration
  - Console output or logs

## Pull Request Checklist

- [ ] Code builds and passes tests
- [ ] Follows code style guidelines
- [ ] Includes relevant documentation updates
- [ ] Has been tested on actual hardware (if applicable)
- [ ] Addresses an existing issue (reference the issue)

## Review Process

- All submissions require review before merging
- Reviewers will check:
  - Code quality and style
  - Test coverage
  - Documentation
  - Performance impact
- Address all review comments before re-requesting review

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for helping improve zephyr-vexriscv! Your contributions make this project better for everyone.
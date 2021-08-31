# Codegex

> A GitHub App built with [Probot](https://github.com/probot/probot) that a Static Analysis Tool for Detecting Bugs in Pull Requests Based on Regular Expression

## Setup

```sh
# Install dependencies
npm install

# Run the bot
npm start
```

## Docker

```sh
# 1. Build container
docker build -t Codegex .

# 2. Start container
docker run -e APP_ID=<app-id> -e PRIVATE_KEY=<pem-value> Codegex
```

## Contributing

If you have suggestions for how Codegex could be improved, or want to report a bug, open an issue! We'd love all and any contributions.

For more, check out the [Contributing Guide](CONTRIBUTING.md).

## License

[ISC](LICENSE) © 2021 EricLee <ericlee54@foxmail.com>

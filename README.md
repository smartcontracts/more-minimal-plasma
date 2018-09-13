# More Minimal Plasma

More Minimal Plasma implements the [Minimal Viable Plasma](https://ethresear.ch/t/minimal-viable-plasma/426) smart contract specification with minor modifications for clarity. More Minimal Plasma is an *unoptimized*, verbose version of Minimal Viable Plasma designed to make the code as clear as possible. This repository holds *only* smart contracts and does not implement the "client" component necessary of any Plasma blockchain.

## Testing

This repository only holds smart contracts and some tests. To run tests, you'll first need to install dependencies:

```
$ make dev
```

Then, you'll be able to run pytest:

```
$ make test
```

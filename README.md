# rELIZA

Hello! Welcome to the GitHub page for rELIZA!

rELIZA is a tool for creating open-domain chatbots on the fly.

This is a fork of Eliza aimed for use on Reddit. It does **not** require sukima!

<sup>something something ship of theseus</sup>

## Table of Contents

1. [Introduction](#introduction)
2. [Setup](#setup)
3. [Configuration](#configuration)
4. [Run](#run)

## Introduction

rELIZA is a framework that provides all of the essentials necessary to build an open-domain chatbot capable of fulfilling basic needs in natural language. This repo holds an implementation for these essentials, including modules that perform core NLP, context building, and more.

## Requirements

For rELIZA to function, you need at least on of:

- Huggingface Transformers (+pytorch/tensorflow) [tensorflow not yet supported, sorry]
- Facebook ParlAI (not yet either, sorry)

## Setup

Then, you will have to clone and setup rELIZA by running these commands:

``$ git clone https://github.com/familiarbreakfast/reliza``

``$ cd reliza``

``$ pip install .``

Alternatively, one can run ``__main__.py`` directly if you don't want to install it.

## Configuration

After the setup is complete, you can use one of the default configurations listed in the ``config`` folder, or you can create your own by using the default as a template. Instructions are on the Github wiki page.

## Run

Then finally, to run the chatbot, all you would need to do is to run this command with your selected config file.

``$ python reliza --config=config/reddit_default.json``

## Todo

- ~~better reddit comment parsing (take whole convo into account)
- clean responses **(in progress)**
- **high priority:** toxic detection
- tune classifier probabilities
- implement bots posting to reddit **(in progress)**
- fix logging (too much garbage)
- clean up any other garbage **(in progress)**
- parlai support (i wanna add blenderbot)
- **high priority:** tensorflow support
- add more options for bots

### License

[GNU Public License version 2.0](LICENSE)

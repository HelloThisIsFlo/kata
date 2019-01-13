# Kata
[![Travis](https://img.shields.io/travis/FlorianKempenich/kata.svg)](https://travis-ci.org/FlorianKempenich/kata) [![PyPI](https://img.shields.io/pypi/v/kata.svg)](https://pypi.org/project/kata/)

## What is a kata and what is `kata` for?
### The wonderful world of Katas
Quick TDD feedback loop.

There is just one single tiny-tini problem...
asdfadsf, but the **problem is when using new language** -> Test setup can be a huge burden. This is where the `kata` tool comes in handy

### Solving the problem
`kata` is based on the incredible work of [swkBerlin](https://github.com/swkBerlin) the software crafting community in Berlin.

To get started with a Kata in a language you might not be entirely familiar with, go to their [swkBerlin/kata-bootstraps repo](https://github.com/swkBerlin/kata-bootstraps) and there you can find ready-to-use, tdd-enabled, projects that'll get you started with your Kata. Simply download the corresponding folder and you're ready to go!

`kata` is a tool that automates this process. No manual downloading, a single command and you're set:
```
kata init my_fantastic_kata java junit5
```

## Quickstart

- **Install:**  
  ```
  pip install kata
  ```
  > **Note:** When first running the kata cli a configuration file is created in `~/.katacli`

---

- **List all languages**:  
  `kata list languages`
- **List all available templates for a language**:  
  `kata list templates LANG`
- **Init a kata with `KATA_NAME` using `TEMPLATE` for `LANGUAGE` in the current directory**:  
  `kata init KATA_NAME LANGUAGE TEMPLATE`

> See the [Configuration](#configuration) section for more information on the available configuration options

---

**Example:** To start a new kata named `bowling`, using the `junit5` template for `java`:  

    `kata init bowling java junit5`



## Motivation
The primary goal of creating this tool was to learn and get familiar with Python.

I had already used the language for small scripts here and there, but I wanted to get a taste of what a real python developement would feel like. For that reason the tool has been built in the same way I'd build professional software:
- The project was developped using **TDD** from the very first line of code
- The project is under semi **Continuous Deployment** (only tags are released)
- Care has been taken to make the code as **readable and maintainable** as possible

What started as a simple project I expected to complete in one afternoon, turned out to take quite a significant amount of my time. By any means, it's a success, the goal was to learn, and I learned a lot. But it is not over, and that's where **you** come in.

I have written a **blog post** about my experience and how **you** can contribute: **[Software Crafter? I need your help!](putlink)**

## Advanced Usage
### Configuration
EXPLAIN HERE ALL THE AVAILABLE CONFIG

### Authentication
explain how it's manual for now and how to get token. Refer to further developpment part on automatic config

## Further developement
### Automated authentication
explain it gave me an idea of Oauth proxy, I'll be working on it
BTW!! THIS (Presenting an idea with support of a nice PlantUML graphe) IS A FANTASTIC IDEA FOR A BLOG POST !! NO NEED TO START THE DEVELOPEMENT BEFORE SHARING IF THE PLAN IS SOLID !!!!!! (And no need to start developping if the plan isn't solid ^_^ )



## Contribution
You are more than welcome to contribute to this project. This is what a community is all about.

### Code changes

All code changes, and features are welcome as long as they don't clutter the main experience.

There is only one requiremenet: Readable tests, showing intent, must be shipped with the code for the modification to be merged.

If you are not sure what that means, don't worry too much, open a pull request whenever you are satisfied with your work, and I'll be happy to work with you so we together find a way to make the intent as clear as possible.
Try it, fantastic experience guaranteed or money back :)

> **Naming convention**:
> To differenciate between the Repository pattern and a Git/Github repo, the following naming convention has been used:
> * `GRepo`: Refers to a Git/Github Repo
> * `Repo`: Refers to a repo in the sense of the Repositry pattern

### Feedback
This is maybe the most important to me, maybe **the most important part of this entire project**: I would love to hear from your feedback. I have written a piece on why that is and laying down the type of feedback I am interested in, give it a look it's a quick read ;) -> **[Software Crafter? I need your help!](putlink)**

The bottom line is: **If you share the belief that readable and maintanable code isn't a luxury but an investment in the long term, I would love to hear your feedback about the _way_ I developped this piece of software.**

If you have any sort of helpful feedback, please **start a discussion by opening an issue, offer some insight with the help of a Pull Request, or even simply send me an email: [Flori@nKempenich.com](mailto:flori@nkempenich.com)**  
Whichever way you choose, I would love to hear from you!

---

## Acknowledgement
* **skwBerlin** for creating kata repo, and playing a good part of who I am I as a developer today
* Templates for all Katas can be found: https://github.com/swkBerlin/kata-bootstraps


---
## Author Information
Follow me on Twitter: [@ThisIsFlorianK](https://twitter.com/ThisIsFlorianK)  
Find out more about my work: [Florian Kempenich — Personal Website](https://floriankempenich.com)


> ### Software Crafter? I need your help!
> **PUT INTO BLOG POST**
> 
> What started as a simple project I expected to complete in one afternoon, turned out to take quite a significant amount of my time.
> By any means, it's a success, the goal was to learn, and I learned a lot. But it is not over, and that's where **you** come in.
> 
> I am sure among you are other people fascinated by how readable code makes everybody's life easier, if that's you, you are a software crafter and I need your help.
> 
> Even though I put my best effort into crafting this piece of software, it still fell short on a couple of aspects: 
> * It took longer than expected
> * The tests ended up being quite verbose
> 
> #### Too much time was spent?
> Find the folder to download, download it, done! Seems simple enough doesn't it? Yet I spent more than 60 hours working on this. Now, that includes a lot of research on the python language itself, the investigation of the Github API, learning about OAuth2, etc...  
> But it still feels too long somehow...
> 
> I would be really interested to have your feedback on this, is this a reasonable amount of time for such a simple project? And if not, what would you have done differently that'd result in the project being finished earlier ?  
> 
> For the sake of clarifying my question: I am evidently not interested in saving some time by skipping tests, not setting up a CD system, or having a botched architecture. These would all defeat the very purpose of the exercise.
> 
> But maybe you think it **is** over-engineered, and **could find a way to keep the same level of quality while reducing the amount of time spent on it?** 
> If that's so, I'd love to hear from you!
> 
> 
> #### Tests are too verbose?
> This one pretty easy to spot early on. I mean go ahead, open a test file, open the code being tested, and just... see for yourself. There is often 2-3 times the amount of test code vs production code!
> 
> Don't get me wrong, I love the result: 
> - I feel at peace when I tag a commit for release
> - Adding a feature is just a fun game of adding a test, implementing the feature, and getting that satisfaction when everything works the first time around when testing in real life
> - Fixing bug is one test-edgecase away
> 
> I love how it feels to work with the software **now**, but I can't help myself but wonder if this isn't slightly overengineered. To relate to the previous point, setting up all these tests took me quite a significant amount of time. Is it time I would save later, not spending hours debugging a particularly corny edge case. I believe that's the case, yes, I've witness it countless time in "real" production code. But then again... that amount of tests... it's a tough sell to a team who's not already seeing how TDD is really a gift you're making to yourself, easy to mistake as a burden.
> 
> So maybe the _way_ I tested things isn't the most efficient one, maybe there **is** too much tests... but I can't seem to identify what I could remove, trim down, while at the same time keeping the same level of confidence I have in this code.
> 
> **In other words, would it be possible to reduce the amount of test code, while keeping the same level of coverage of behavior? If so, how would you proceed?**
> 
> By _coverage of behavior_, I do not mean _code coverage_, rather the coverage of every branch of execution that was brought when building the project with TDD.
> 
> #### Your help is very much appreciated
> If you have any sort of helpful feedback on the aforementionned topics, please **start a discussion by opening an issue, offer some insight with the help of a Pull Request, or even simply send me an email: [Flori@nKempenich.com](mailto:flori@nkempenich.com)**  
> Whichever way you choose, I would love to hear from you!


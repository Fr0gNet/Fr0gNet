# Fr0gNet

![fr0gNet-animated-logo](https://github.com/user-attachments/assets/8c86148f-f49a-4551-b673-fa8406b898b0)

Fr0gNet is a decentralized web file system for uncensorable ID-addressed websites and content.
Built on Stellar, Fr0g turns the network into a global, censorship-resistant data layer where content can’t be silently altered, taken down, or forgotten.
### fr0g IDs
A *fr0g ID* act like a "domain" that links directly to on-chain files and content.
IDs are deterministic, globally resolvable, and independent of any specific client implementation.
An example of fr0g ID: **fr0gdvkapv7ko5cl65qgpekkewgo2n2vl3j7ldf2x5xtgkbkucohsvgvszcg**
You get a random keypair (fr0g ID + secret) , If you bind some content and share its corresponding fr0g ID, anyone can view it on a browser. *Content you bind (like HTML code) can be globally browsed by anyone have the fr0g ID (also if he haven't fr0g installed*) .
With your secret,if you want, you can edit or remove the content, maintaining the same fr0g ID.
It is possible to bind multiple files to a single ID, every file will have an index (#1,#2). The content at the index 0 act as default content of the ID (like an index.html) and by default the content will be uploaded at 0.To bind content to a different index you must specify esplicitically. look at *bind multiple files to a single fr0g ID*
## Architecture
**fr0g is essentially an application-layer protocol built on Stellar.**
Stellar is used as the underlying consensus, transaction, and data-availability layer, while fr0g defines higher-level primitives for permanent, censorship-resistant contents
### Layered Architecture
```
┌─────────────────────────────────────────────┐
│ fr0g Clients │
│ (CLI, Web, SDKs, custom applications) │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ fr0g Application Layer │
│ • fr0g ID resolution │
│ • Content addressing & metadata │![grok-image-e650ab40-9284-465a-9ec2-711d27b3eda6(3)](https://github.com/user-attachments/assets/72153e2e-90d4-4bfa-bdc7-d93913acf5c8)


https://github.com/user-attachments/assets/25eb8ac3-0410-40f6-8c31-1b28cc527281



https://github.com/user-attachments/assets/9784d809-d04c-4cc5-b8ed-fe72e31cc8ac


│ • App & file primitives │
│ • Client-agnostic protocol rules │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Stellar Network │
│ • Consensus & finality │
│ • Transaction ordering │
│ • On-chain data storage │
│ • Global availability │
└─────────────────────────────────────────────┘
```
---
---
### On-chain Data Model
fr0g encodes application state, file references, and metadata directly on-chain using Stellar transactions.
Once published, data becomes:
* **immutable**
* **publicly verifiable**
* **censorship-resistant**
Clients interpret this data according to fr0g’s logic
---
### Clients
fr0g is **client-agnostic** by design.
Any program, application, or script that follows the protocol can act as a fr0g client.
Official apps like Fr0gNet are provided for convenience, but:
* no client is privileged
* no client is required
* the protocol remains fully permissionless
---
### Getting Started and examples for developers:
The core of fr0g is written in Python as a one pure-python file: fr0g.py
Just put **fr0g.py** in a folder then write some Python in the same folder:
## EXAMPLE: Upload things
In the following example we create a new fr0g ID and upload some HTML code
```
import fr0g
id, secret = fr0g.random_keypair(enabled=True)
fr0g.upload(b"<h1>Hello World</h1>", secret)
```
That's all. Now you have a ID that refelcts your content, it works like as a domain
##
### Security & Trust Model
* Stellar provides consensus, ordering, and finality
* fr0g adds semantic meaning at the application layer
* Trust is minimized to cryptographic verification and protocol rules
* No centralized infrastructure is required to read or publish data

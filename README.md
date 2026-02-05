# Fr0gNet

**[Fr0gNet Browser](https://fr0gnet.github.io/Fr0gNet/frontend/browser)**

### Fr0g

Fr0g is an application/layer protocol build on Stellar that enables a decentralized web file system for uncensorable ID-addressed websites and content

Fr0g turns the network into a global, censorship-resistant data layer where content can’t be silently altered, taken down, or forgotten: the **Fr0gNet**


### fr0g IDs
A *fr0g ID* act like a "domain" that links directly to on-chain files and content.
IDs are deterministic, globally resolvable, and independent of any specific client implementation.

You get a random keypair (fr0g ID + secret) ; if you bind some content and share its corresponding fr0g ID, anyone can view it on a browser. *Content you bind (like HTML code) can be globally browsed by anyone have the fr0g ID (also if he haven't fr0g installed*) .
With your secret,if you want, you can edit or remove the content, maintaining the same fr0g ID.

*An example of fr0g ID*
**fr0gdvkapv7ko5cl65qgpekkewgo2n2vl3j7ldf2x5xtgkbkucohsvgvszcg** 

It is possible to bind multiple files to a single ID, every file will have an index (#1,#2).

The content at the index 0 act as default content of the ID (like an index.html) ; by default the content will be uploaded at 0.

To bind content to a different index you must specify esplicitically.

### Getting Started and examples for developers:

The core of fr0g is written in Python as a one pure-python file: fr0g.py

## EXAMPLE: Upload things

In the following example we create a new fr0g ID and bind some HTML code to it using Python

```bash
$ git clone https://github.com/Fr0gNet/Fr0gNet
$ cd Fr0gNet/core
$ python3
```

```python
>>> import fr0g
>>> fr0g_ID, fr0g_secret = fr0g.random_keypair(enabled=True)
>>> print(fr0g_ID)
# fr0gvlelionz5su2ukloaoeyxvetgygkceeu2v3ozqaid6ipslg4emyfihcg
>>> fr0g.upload(b"<h1>Hello Fr0gNet</h1>", fr0g_secret, index=0) 
```
That's all.

Use *fr0g.get_content(fr0g_ID)* to get the content back.

Re-upload to index=0 to edit (or remove) the content: *fr0g.upload(b"Heeeelllo",fr0g_secret,index=0)*

`b''` deletes the content.

### Maximum file size

Using fr0g normally, the maximum sum of file size per-iD should not exceed 60KB.
you may receive errors during upload if you are close to this limit.

## Browse the Fr0gNet with *fr0g leaps*

*Leaps* are like "magic doors" embedded in HTML links or buttons in your browser. They give you direct access to the Fr0gNet.

The HTML file does **not** need to be hosted on localhost — it works perfectly fine even from a local file (`file:///`).

Here is the HTML code that creates a clickable link to access the Fr0gNet.

It shows the content in a new tab (just replace the `fr0g-ID` value with your own):

```html
<a href="javascript:void(0)"
   fr0g-ID="fr0g2fi7jofxqjfayl7o7pkanes7xjsgijylbbud4atm6v2vp2mq4mjapnbg"
   onclick="let id=this.getAttribute('fr0g-ID');let stellar=id.substring(4).split('').reverse().join('').toUpperCase();console.log('Stellar addr:', stellar);fetch('https://horizon-testnet.stellar.org/accounts/'+stellar).then(r=>{if(!r.ok)throw new Error('Account not found: '+r.status);return r.json()}).then(d=>{console.log('Data keys:', Object.keys(d.data));if(!d.data || Object.keys(d.data).length===0)throw new Error('No data found for this fr0g ID – make sure it is enabled and content has been uploaded');let chunks=[],len=0;Object.entries(d.data).forEach(([k,v])=>{if(k.startsWith('fr0g:f0c')){let parts=k.match(/fr0g:f0c(\d+):(\d+)/);console.log('Key:', k, 'match:', parts);if(parts){let cn=parseInt(parts[1]);chunks[cn-1]=atob(v);len=len||parseInt(parts[2]);}}});let content=chunks.join('').slice(0,len).replace(/\xff+$/,'');console.log('Chunks length:', chunks.length, 'Len:', len, 'Content:', content);if(!len || content.length === 0)throw new Error('No content chunks found for this fr0g ID at index 0 – verify upload with set_as_index=True');let w=window.open('about:blank');w.document.open();w.document.write(content);w.document.close();}).catch(e=>{console.error('Error loading fr0g:',e);alert('Failed to load content: ' + e.message);});return false;">

Enter the Fr0gNet!

</a>
```


## Browse the Fr0gNet with Fr0gNet Browser

[https://fr0gnet.github.io/Fr0gNet/frontend/browser/](https://fr0gnet.github.io/Fr0gNet/frontend/browser/)


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
│ • Content addressing │
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
### Security & Trust Model
* Stellar provides consensus, ordering, and finality
* fr0g adds semantic meaning at the application layer
* Trust is minimized to cryptographic verification and protocol rules
* No centralized infrastructure is required to read or publish data
### License

Copyright 2026 0ut0flin3

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software

distributed under the License is distributed on an "AS IS" BASIS,

WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and

limitations under the License.

### Contact

0ut0flin3@protonmail.com


### Donate

XLM: GDJDYV2WWEWXR4TUQY3TOCA5AF55PXNKRDQT7U2T3C6ZKARMOHYLPHWZ

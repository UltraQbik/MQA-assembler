# MQA assembler
Mini Quantum Assembler - it assembles Mini Quantum's assembly instructions.<br/>
Mini Quantum - MQ - 8bit CPU that was made entirely in Scrap Mechanic, using vanilla logic gates.<br/>
Information on MQ can be found on my discord servers:<br/>
- [RU] ['MQ' discord forum post](https://discord.com/channels/863390692591665152/1119025865968341002)
- [EN] ['MQ' discord forum post](https://discord.com/channels/860450204000059412/1204119619036516352)
- [EN] ['MQ' discord forum post](https://discord.com/channels/532624495081422869/1171195234391167067) but from [@codemaker4](https://github.com/codemaker4) discord server, and less maintained
<br/>If you want just the instruction set go [here](https://docs.google.com/spreadsheets/d/1Sl82E1pRsVYuFbP9roWOJOsSJ4JLtFiOXaD3Rq9oaJI/edit#gid=0)
<br/>If you want the computer check this [repository](https://github.com/UltraQbik/SMC-MQ-CPU)

# Compatibility
This repo will work with python 3.10+ (doesn't work on python ≤ 3.9 because of type hinting syntax)<br/>
No additional libraries required, it uses the default ones, preinstalled with python.
# Building
1. git clone https://github.com/UltraQbik/MQA-assembler
2. cd MQA-assembler
3. python -m build
4. pip install dist/\*.whl
<br/>Now you can run it through either mqa or python -m mqa
# Code examples
Code examples are located in directory 'examples', there you will find some examples of assembly code written for MQ's

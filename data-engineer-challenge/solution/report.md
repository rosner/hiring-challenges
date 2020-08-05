> write a report: what did you do? what was the reasons you did it like that?

I approached the challenge in multiple steps to solve one thing at a time.

First I had to read it carefully and deconstruct what I actually had to achieve and what was expected from me. On top I needed to get a feeling for the time constraints and how that would fit into my day (Yeahi :baby:, :diaper: etc.).

Below is a rough summary of the steps I took. I'm describing some of the important steps in more detail afterwards.
1. Research Kafka:
    - how does it work
    - what are common use cases
    - how does it compare to let's say Kinesis
    - how does the ecosystem look like, i.e. what are its APIs, ksqlDB
    - how does it relate to the "big data framework" mentioned in the challenge ReadMe
    - how can I interact with it using Python as my language of choice
2. Get Kafka running on my local machine:
    - Docker vs. homebrew vs. x?
3. Follow the challenge instructions regarding the example data
    - do the instructions actually work or do I need to debug/bounce back for questions or clarifications
4. Execute some example kafka code to get an understanding of the API and approaches to be used
5. Work on the algorithm for simple counting in isolation
    - extract a subset of the data
6. Integrate algorithm into the Kafka interaction boilerplate
7. Provide project setup documentation and prepare report
    

# 1. Research Kafka:
## - how does it relate to the "big data framework" mentioned in the challenge ReadMe
This was actually fun to _decipher_ as I brushed up my knowledge about the ecosystem when it comes to stream processing frameworks like Spark, Samza, Storm etc.
## - how does the ecosystem look like, i.e. what are its APIs, ksqlDB
This was important for me to understand in order to find the respective boilerplate that uses the API I felt was most appropriate for this challenge, namely the Consumer/Producer APIs. I also peaked into the Streams API, however from what I could gather there's no Python "version" and I didn't want to invest time to code in Java due to the simple fact that I'm faster in Python.
## - how can I interact with it using Python as my language of choice
This was mainly about which python packages are out there that could be used to connect to a Kafka cluster. There's a bunch of them available with pros and cons. I made a quick decision here to choose the [confluent-kafka|https://pypi.org/project/confluent-kafka/] which is maintained by Confluent itself.
On a side note I (re)discovered [Faust from Robinhood|https://github.com/robinhood/faust] which (still) looks intriguing.

# 2. Get Kafka running on my local machine:
My very quick decision was to go with homebrew. I don't have Docker installed on my old machine. I also didn't know what to expect from the challenge down the line in terms of amount of data and processing speed. So I decided to skip the "middle-man" Docker for [simplicity's sake|https://success.docker.com/article/getting-started-with-kafka].

# 4. Execute some example kafka code to get an understanding of the API and approaches to be used
Confluent has decent [example code on Github|https://github.com/confluentinc/examples/tree/5.5.1-post/clients/cloud/python]. This worked as advertised so I decided to use it.

# 5. Work on the algorithm for simple counting in isolation
## - extract a subset of the data
For quick iteration (and as suggested in the challenge ReadMe) I extracted the `ts` and `uid` property from 200k messages and stored them in a csv file. This helped me come up with a first version of my basic solution. After integrating it with the Kafka boilerplate code mentioned above I found out how to disable the auto commit. This acted as my test environment to tweak my algorithm. I simply set `enable.auto.commit` to `false` in the consumer config. This means that the consumer will always process messages from the start.

--- 

> research and use of suitable data structure for a specific use case. explain which and why.

My basic solution uses a list as an accumulator and a variable that holds the current minute under process. All user ids are captured and as soon as a new minute is detected the content of the accumulator is converted into a set and thus contains the unique user ids. Everything is printed to stdout at this point. The accumulator is emptied and the variable for the minute under process is set to the newly observed minute.

Why did I built it this way? Because it worked in the first attempt. 

> when creating e.g. per minute statistics, how do you handle frames that arrive late or frames with a random timestamp (e.g. hit by a bitflip), describe a strategy?

I'm sure my basic implementation wouldn't work with variations of these edge cases. I can think of different strategies:
    
- If this is an internal use case for reporting one could try and agree on some form of accuracy metric with stakeholders. You'd have to change the implementation to detect random or delayed messages and report those separately. Ideally close to where the statistics are being reported. This way at least stakeholders could see metrics side by side and consider those when making decisions.

- Use different data structures and algorithms. One approach I can think of here would be to use a dictionary with the minutes (e.g., as formatted string) as key and the value would be the same list of user ids. Further I would move away from the very simple conditional that checks for a new minute. Instead I can think of some threshold based condition that checks how often a new minute has been seen. 
The downside of this approach might be though that the time it takes to output result would increase. However I think with what I roughly described above one would have a more fine grained control to tweak the parameters of when to display data and how big the window would be for delayed messages. 

    As for random timestamps, I can think of some sort of "trash" key which would be reported as well. This way it could be monitored and if there's high variance it could be an alarming signal that something might off and it should be investigated.

---

> scalability: explain how you would scale your approach
I assume that _scale_ here means scaling in the context of consuming Kafka messages. If my research and understanding is correct then there's two metaphorical knobs to turn:

Topic partitioning and multiple consumers/consumer groups
I went with simply one partition for the topic `doodle-challenge`. To support a higher throughput a basic approach I would try is to increase the number of partition for the topic where the messages are written to. This would later on allow me to use multiple consumers grouped in so called consumer groups to process from specific partitions respectively. Kafka would under the hood make sure to send messages from one partition to a specific consumer. 
## Interview project



Imagine if we have a YouTube-like video website, where many users are watching videos that we host. 

- Whenever a user is watching a video, they generate events: every 10s, every time they seek/skip, every time they start/pause the video they are watching, or if they move to another page/video.
- Our streaming servers also generate an event every time a video is streamed, stopped streaming, etc

All these events get collected and processed fully by our analytics infrastrucutre.

In this project you need to setup a simulation in which you have services simulating users, and services simulating our streaming servers. The two will generate events and you will need to setup the analytics infrastructure that will process this. Here are the details


### Users
Setup a micro-service that simulates users. 
- Each service instance is responsible for simulating one user. 
- The micro-service is spun up programatically via an HTTP endpoint, example …/addOneUser
- It will randomly decide to simulate an action (example playing a video) and the duration of that action. When the duration is done, it will randomly pick another action to simulate (example opening a different video). Not all actions have duration, and some of them have some attributes (e.g. the video ID that is being chosen)… in such cases these are picked randomly. 
- At one point or another, the micro-service will randomly pick to stop (i.e. simulating the user is closing their browser). In which case it will submit the relevant event and the service will shutdown. Remember, this service is only representing 1 user, so basically that user has ended their session but other users might be doing other stuff (each simulated concurrently by their own micro-service instance).

### Streaming servers
Setup an auto-scaling cluster that simulates the streaming servers. A server would handle requests from x users (e.g. 100) and when nearing capacity the service would spin up another node in the cluster to reduce the load. Think Kubernetes or elastic load balancer with some threshold.

- The server fires events when they receive an action from the user, example start streaming a video, or stop streaming a video etc
- When the user seeks their video, the server will start streaming that video from a different point, sending such event
- The server fires an event every 10 seconds when user is playing continuously
- Server doesn’t know about the events or actions the user is planning to take. For example, a user might have decided to play the video for 1 min and then exit. The server wouldn’t know. They will only know that the user started playing. Then they will know when the user stops/exits. But the server won’t know initially that the user planned to watch the video for only 1 min. It is similar to for example Youtube!

### Simulation orchestrator
This is a simple long living service, that calls the end point to create new users randomly, within some rules. The service should generate users in accordance with a sine wave. Meaning, it will initially generate very few users, then ramp up, then slow down, then ramp up etc. Make it easy for me to adjust the two parameters that control this: the max height of the wave (e.g. at its max will be generating 100 users per second), and the width of the wave (how quickly it will ocilate, for example it will move from peak to slowing down and back to peak every 1 min). These should be adjustable mid simulation (either via simple html ui sliders or via an endpoint I can call)
In addition there is one more parameter: random error factor. This should be adjustable. When this is zero, the new users will not make errors when firing their events. However when this 1, the event data  becomes completely erroneous.


### Datawarehouse, Lake or Lakehouse

- Setup an event store of your choosing that can handle this scale/load fluently
- Setup an open source BI tool of your choosing and do some dashboards to monitor the system
- Define some sensible metrics and interesting stats to monitor the system
- Allow me as a product person to dashboard or query for answers to my own questions
- Setup data quality metrics. What are the expectation in our data? Define such expectations and measure how compliant our event data is 





### Please make sure you:

* Please break down the project into 3-4 milestones, and create a PR for each. Please do this first thing! Each PR will be on it’s own branch, e.g. Release 1, Release 2 etc. Or preferably you can give them meaningful names.
* When you’re done with a milestone, squash merge it into the next PR. E.g. you’re done with release1, squash merge release1 into release2. From that point on please continue working on release2. Don’t go back to release1 and change it! Any bugs you would like to fix, simply fix them in release2. Once it’s done, squash merge it into release3 etc…
* Please keep all your branches and PRs, no need to delete anything
* Merge the final release into main
* Contribute directly to this repo (i.e. avoid creating fork)
* Please include few screenshot or screen recording of the final result. Sometimes I need to make sure that what I see on my end is similar to what you're getting.
* Please include running instructions!

If you’re unclear about something you can always write down a comment in the relevant PR: I am unsure if I am required to do x or y, I am assuming it is x and carrying on. However please refer back to the instructions to double check that the answer wasn’t given already. Don’t wait for answers, just use common sense keep going!

Let us know when you’re done!

Thanks and looking forwards for a brilliant submission!

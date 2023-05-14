# temporalHop

Yet another attempt at temporal consistency :)

This is a method of achieving img2img temporal consistency in automatic1111 across a long video without using eb-synth. This utilizes the phenomena that stable diffusion seems to be more consistent when creating multiple frames in a single image.

This works by creating a template image of 2x2 frames from the video. For each frame in the video, we take 3 control frames that have been transformed via img2img, and vary the bottom right frame, then only in-paint the bottom right frame.

Input             |  Output
:-------------------------:|:-------------------------:

![ezgif-4-12d620db27](https://github.com/ultrafro/temporalHop/assets/3029964/c7c25508-d34b-4411-aec4-0a15c7268f54)  |  ![ezgif-4-bdfe60e5a5](https://github.com/ultrafro/temporalHop/assets/3029964/edb63905-5a25-499b-8198-886eef6b1cef)


**Input:**

![ezgif-4-12d620db27](https://github.com/ultrafro/temporalHop/assets/3029964/c7c25508-d34b-4411-aec4-0a15c7268f54)

**Output:**

![ezgif-4-bdfe60e5a5](https://github.com/ultrafro/temporalHop/assets/3029964/edb63905-5a25-499b-8198-886eef6b1cef)

**Settings:**
- model: Anything v3
- mode: img2img
- prompt: cyberpunk, ((anime)), sci-fi, glowing green eyes, robot, plain t-shirt, masterpiece, sharp lines
- negative prompt: ugly face
- controlnet: HED soft-edges

### Installation:
Copy `temporalHop.py` into `/scripts`

### Using it:

- Open the temporal hop script:

![image](https://github.com/ultrafro/temporalHop/assets/3029964/1333da9d-5042-4a40-bf0d-a9796cec6d29)

- drag in a vertical video

![Untitled (7)](https://github.com/ultrafro/temporalHop/assets/3029964/9fec0f2a-9624-4a19-91c5-b984b5b77e5a)

- press make template

![Untitled (8)](https://github.com/ultrafro/temporalHop/assets/3029964/f6d3328f-4446-4953-bde4-bccc5eba1dbe)

-  Edit that template using img2img (ideally using a control-net process). Make sure to copy over the seed, and set the resolution to 432 x 768. TODO: be able to control this

![Untitled (9)](https://github.com/ultrafro/temporalHop/assets/3029964/ff911662-99e0-465d-a93c-3cea3ae44e54)

- Press “prepare inpainting batch”. This creates an `inputs`, `outputs`, and `masks` folder for you to use in img2img batch

![Untitled (10)](https://github.com/ultrafro/temporalHop/assets/3029964/ae50b5e1-b0a3-4e75-a0ec-d4a15fc44026)

- Click on “batch” in im2im2, make sure to maintain the same settings
copy over the path in the folder to /inputs, /outputs, and /masks

![Untitled (11)](https://github.com/ultrafro/temporalHop/assets/3029964/17da8b99-136c-4104-ab53-6de23d340832)

- press "Recombine video"

![Untitled (14)](https://github.com/ultrafro/temporalHop/assets/3029964/25bf9e30-4c79-4a22-a497-183145c8fb1a)

### Todo:
- do more research into what's out there
- make this into an extension
- allow for output resolution control
- make it work with videos of any aspect ratio


### How it works:

example input:

![Untitled (12)](https://github.com/ultrafro/temporalHop/assets/3029964/98f8b530-e2c9-4459-9874-8bd672a3384e)

example inpainting mask:

![Untitled (13)](https://github.com/ultrafro/temporalHop/assets/3029964/1e80bdf0-a841-4555-acfa-7694dfea4655)


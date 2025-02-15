# -- coding: utf-8 --`
import argparse
import os
# engine
from stable_diffusion_engine import StableDiffusionEngine
# scheduler
from diffusers import LMSDiscreteScheduler, PNDMScheduler
# utils
import cv2
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import datetime


def main(args):
    if args.seed is not None:
        np.random.seed(args.seed)
    if args.init_image is None:
        scheduler = LMSDiscreteScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            tensor_format="np"
        )
    else:
        scheduler = PNDMScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            skip_prk_steps = True,
            tensor_format="np"
        )
    engine = StableDiffusionEngine(
        model = args.model,
        scheduler = scheduler,
        tokenizer = args.tokenizer
    )
    image = engine(
        prompt = args.prompt,
        init_image = None if args.init_image is None else cv2.imread(args.init_image),
        mask = None if args.mask is None else cv2.imread(args.mask, 0),
        strength = args.strength,
        num_inference_steps = args.num_inference_steps,
        guidance_scale = args.guidance_scale,
        eta = args.eta
    )
    #cv2.imwrite(args.output, image)
    # convert from openCV2 to PIL. Notice the COLOR_BGR2RGB which means that 
    # # the color is converted from BGR to RGB
    color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image=Image.fromarray(color_coverted)
    metadata = PngInfo()
    metadata.add_text("prompt", args.prompt)
    metadata.add_text("timestamp", datetime.datetime.now().isoformat())
    metadata.add_text("tool", "stable diffusion openvino 1.4")
    metadata.add_text("dimension", "512x512")
    metadata.add_text("seed", str(args.seed))
    metadata.add_text("num-inference-steps", str(args.num_inference_steps))
    metadata.add_text("strength", str(args.strength))
    metadata.add_text("guidancescale", str(args.guidance_scale))
    pil_image.save(args.output, "PNG", pnginfo=metadata) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # pipeline configure
    parser.add_argument("--model", type=str, default="bes-dev/stable-diffusion-v1-4-openvino", help="model name")
    # randomizer params
    parser.add_argument("--seed", type=int, default=None, help="random seed for generating consistent images per prompt")
    # scheduler params
    parser.add_argument("--beta-start", type=float, default=0.00085, help="LMSDiscreteScheduler::beta_start")
    parser.add_argument("--beta-end", type=float, default=0.012, help="LMSDiscreteScheduler::beta_end")
    parser.add_argument("--beta-schedule", type=str, default="scaled_linear", help="LMSDiscreteScheduler::beta_schedule")
    # diffusion params
    parser.add_argument("--num-inference-steps", type=int, default=32, help="num inference steps")
    parser.add_argument("--guidance-scale", type=float, default=7.5, help="guidance scale")
    parser.add_argument("--eta", type=float, default=0.0, help="eta")
    # tokenizer
    parser.add_argument("--tokenizer", type=str, default="openai/clip-vit-large-patch14", help="tokenizer")
    # prompt
    parser.add_argument("--prompt", type=str, default="Street-art painting of Emilia Clarke in style of Banksy, photorealism", help="prompt")
    # img2img params
    parser.add_argument("--init-image", type=str, default=None, help="path to initial image")
    parser.add_argument("--strength", type=float, default=0.5, help="how strong the initial image should be noised [0.0, 1.0]")
    # inpainting
    parser.add_argument("--mask", type=str, default=None, help="mask of the region to inpaint on the initial image")
    # output name
    parser.add_argument("--output", type=str, default="output.png", help="output image name")
        # diffusion params
    parser.add_argument("--batch", type=int, default=1, help="run prompts in batch N times")
    args = parser.parse_args()
    output = args.output
    if args.batch > 1:
        for i in range(1,args.batch+1,1):
            args.output = output.replace(".png", "_") +  str(i) + ".png"
            print(args.output)
            main(args)
    else:
        print(args.output)
        main(args)


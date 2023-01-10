#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import os
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    #run = wandb.init(job_type="basic_cleaning")
    #run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    #artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Downloading artifact")
    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    local_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    # Drop outliers
    logger.info("Dropping outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    logger.info("Convert last_review to datetime format")
    df['last_review'] = pd.to_datetime(df['last_review'])
    # Drop outliers based on lat and long
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Save cleaned artifact to W&B
    logger.info("Save cleaned data to W&B")
    df.to_csv("clean_sample.csv", index=False)
    
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(args.output_artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Path to input artifact in W&B",
        required=True,
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Path to output artifact in W&B",
        required=True,
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of output artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price threshold to cut outliers",
        required=True,
    )
    
    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price threshold to cut outliers",
        required=True,
    )

    args = parser.parse_args()

    go(args)

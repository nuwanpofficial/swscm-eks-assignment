#!/usr/bin/env python3
import os

import aws_cdk as cdk

from eks_proj.eks_proj_stack import EksProjStack


app = cdk.App()
EksProjStack(app, "EksProjStack",            
    )

app.synth()

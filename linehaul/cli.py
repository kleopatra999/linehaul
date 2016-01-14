#!/usr/bin/env python3.5
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

import click

from ._click import AsyncCommand
from ._server import Server
from .bigquery import BigQueryClient
from .core import Linehaul


@click.command(cls=AsyncCommand)
@click.option("--bind", default="0.0.0.0")
@click.option("--port", type=int, default=512)
@click.option("--token")
@click.option("--account")
@click.option("--key", type=click.File("r"))
@click.argument("table")
@click.pass_context
async def main(ctx, bind, port, token, account, key, table):
    bqc = BigQueryClient(*table.split(":"), client_id=account, key=key.read())

    with Linehaul(token=token, bigquery=bqc, loop=ctx.event_loop) as lh:
        async with Server(lh, bind, port, loop=ctx.event_loop) as s:
            try:
                await s.wait_closed()
            except asyncio.CancelledError:
                click.echo(click.style("Shutting Down...", fg="yellow"))

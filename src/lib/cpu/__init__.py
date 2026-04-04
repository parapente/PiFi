from lib.cpu.base import ZCpuBase
from lib.cpu.handlers_2op import ZCpu2OpHandlers
from lib.cpu.handlers_1op import ZCpu1OpHandlers
from lib.cpu.handlers_0op import ZCpu0OpHandlers
from lib.cpu.handlers_var import ZCpuVarHandlers
from lib.cpu.handlers_ext import ZCpuExtHandlers
from lib.container.container import Container


class ZCpu(ZCpuBase, ZCpu2OpHandlers, ZCpu1OpHandlers, ZCpu0OpHandlers, ZCpuVarHandlers, ZCpuExtHandlers):
    pass


Container.register("ZCpu", ZCpu)

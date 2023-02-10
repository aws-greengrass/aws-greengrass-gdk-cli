from .BuildSystem import BuildSystem
from .Zip import Zip    

build_system = BuildSystem()
build_system.register(Zip())
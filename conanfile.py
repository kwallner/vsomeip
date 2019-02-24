from conans import ConanFile, tools, CMake
from conans.util import files
import os

class vsomeipConan(ConanFile):
    name = "vsomeip"
    version = "2.10.21"
    license = "MPL2.0"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    description = "An implementation of Scalable service-Oriented MiddlewarE over IP."
    author = "Bayerische Motoren Werke Aktiengesellschaft (BMW AG); modified by Karl Wallner <kwallner@mail.de>"
    url = "https://github.com/GENIVI/vsomeip"
    scm = { "type": "git", "url": "auto", "revision": "auto" }
    no_copy_source = True
    options = {"shared": [False,True], "fPIC": [False,True]}
    default_options = { "shared" : True, "fPIC" : True }
    default_user = "kwallner"
    default_channel = "testing"
    
    def requirements(self):
        self.requires("boost/1.69.0@%s/%s" % (self.user, self.channel))

    def build(self):
        cmake = CMake(self)
        # ENABLE_SIGNAL_HANDLING
        cmake.configure()
        cmake.build()
        cmake.install()
        cmake.test()
        
    def package_info(self):
        self.env_info.vsomeip_DIR = os.path.join(self.package_folder, "setup")

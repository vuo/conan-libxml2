from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class Libxml2Conan(ConanFile):
    name = 'libxml2'

    source_version = '2.9.10'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libxml2'
    license = 'http://xmlsoft.org/FAQ.html#License'
    description = 'A library for reading and writing XML'
    source_dir = 'libxml2-%s' % source_version

    build_x86_dir = '_build_x86'
    build_arm_dir = '_build_arm'
    install_x86_dir = '_install_x86'
    install_arm_dir = '_install_arm'
    install_universal_dir = '_install_universal_dir'

    def source(self):
        tools.get('http://xmlsoft.org/sources/libxml2-sources-%s.tar.gz' % self.source_version,
                  sha256='9c332062611b88e773d81c070364525c3f0cefa0ecaac902dcedb72e6e44c978')

        self.run('mv %s/Copyright %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        # The LLVM/Clang libs get automatically added by the `requires` line,
        # but this package doesn't need to link with them.
        autotools.libs = []

        autotools.flags.append('-Oz')

        if platform.system() == 'Darwin':
            autotools.flags.append('-isysroot %s' % self.deps_cpp_info['macos-sdk'].rootpath)
            autotools.flags.append('-mmacosx-version-min=10.11')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libxml2.dylib')

        common_configure_args = [
            '--quiet',
            '--disable-static',
            '--enable-ipv6=no',
            '--enable-shared',
            '--with-sax1',
            '--with-threads',
            '--with-xpath',
            '--without-c14n',
            '--without-debug',
            '--without-ftp',
            '--without-iconv',
            '--without-iso8859x',
            '--without-legacy',
            '--without-lzma',
            '--without-modules',
            '--without-pattern',
            '--without-push',
            '--without-python',
            '--without-reader',
            '--without-regexps',
            '--without-schemas',
            '--without-schematron',
            '--without-valid',
            '--without-writer',
            '--without-xinclude',
        ]

        env_vars = {
            'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
            'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
        }
        with tools.environment_append(env_vars):
            build_root = os.getcwd()

            self.output.info("=== Build for x86_64 ===")
            tools.mkdir(self.build_x86_dir)
            with tools.chdir(self.build_x86_dir):
                autotools.flags.append('-arch x86_64')
                autotools.link_flags.append('-arch x86_64')
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=common_configure_args + [
                                        '--prefix=%s/%s' % (build_root, self.install_x86_dir),
                                    ])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

            self.output.info("=== Build for arm64 ===")
            tools.mkdir(self.build_arm_dir)
            with tools.chdir(self.build_arm_dir):
                autotools.flags.remove('-arch x86_64')
                autotools.flags.append('-arch arm64')
                autotools.link_flags.remove('-arch x86_64')
                autotools.link_flags.append('-arch arm64')
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=common_configure_args + [
                                        '--prefix=%s/%s' % (build_root, self.install_arm_dir),
                                        '--host=x86_64-apple-darwin15.0.0',
                                    ])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        tools.mkdir(self.install_universal_dir)
        with tools.chdir(self.install_universal_dir):
            self.run('lipo -create ../%s/lib/libxml2.%s ../%s/lib/libxml2.%s -output libxml2.%s' % (self.install_x86_dir, libext, self.install_arm_dir, libext, libext))

        self.copy('*.h', src='%s/include/libxml2' % self.install_x86_dir, dst='include')
        self.copy('libxml2.%s' % libext, src='%s' % self.install_universal_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['xml2']

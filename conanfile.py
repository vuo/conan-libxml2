from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

class Libxml2Conan(ConanFile):
    name = 'libxml2'
    version = '2.9.2'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libxml2'
    license = 'http://xmlsoft.org/FAQ.html#License'
    description = 'A library for reading and writing XML'
    source_dir = 'libxml2-%s' % version
    build_dir = '_build'

    def source(self):
        tools.get('http://xmlsoft.org/sources/libxml2-sources-%s.tar.gz' % self.version,
                  sha256='df08982aad4c9d98ac8b064add327b23eaeba3e3ca4be311bd58985760bb6cb0')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-mmacosx-version-min=10.8')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libxml2.dylib')
            autotools.configure(configure_dir='../%s' % self.source_dir,
                                args=['--quiet',
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
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])

    def package(self):
        self.copy('*.h', src='%s/include/libxml2' % self.build_dir, dst='include')
        self.copy('libxml2.dylib', src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['xml2']

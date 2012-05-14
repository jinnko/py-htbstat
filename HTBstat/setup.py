#! /usr/bin/env python
#
# setup.py
#
#  easytelnet is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Foobar; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from distutils.core import setup
import sys, os

setup(name = "HTBstat",
      version = "0.2.3-dor2",
      description = "Helper library to make rrd pictures from HTB stats",
      author = "Dmytro O. Redchuk",
      author_email = "dor@ldc.net",
      license = "LGPL",
      url = "http://www2.ldc.net/~dor/",
      packages = [ '.' ]
)

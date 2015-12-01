import numpy,sys,glob,argparse,os
from PIL import Image
from subprocess import check_call

parser = argparse.ArgumentParser(description='Build sweeping zbuffer images')

parser.add_argument('bmp', help='The BMP file of the MBMP chunk of the scene you want to convert')
parser.add_argument('zbmp', nargs='?', help='The (decompressed) ZBMP chunk of the scene you want to convert (defaults to {BMPARG}.ZBMP)')
parser.add_argument('-o','--output', metavar='GIF', nargs='?', default='anim.gif', help='Filename to write the animated GIF to')
parser.add_argument('--zmin', metavar='N', nargs='?', type=int, help='Override the min depth of the GIF (0-65536)')
parser.add_argument('--zmax', metavar='N', nargs='?', type=int, help='Override the max depth of the GIF (0-65536)')
parser.add_argument('--speed', metavar='HSECS', nargs='?', type=int, default=5, help='Hundredths of seconds between frames')
parser.add_argument('--steps', metavar='N', nargs='?', type=int, default=100, help='Number of frames to render')
parser.add_argument('--last-frame', metavar='HSECS', type=int, nargs='?', default=200, help='Extra hundredths of seconds to show last frame for')
parser.add_argument('--skip-gif', action='store_true', help="Don't create the final GIF, just extract the frames")
parser.add_argument('-r','--reverse', action='store_true', help="Build the GIF from back to front, instead of front to back")

args = parser.parse_args()

def correctPathCase(path):
	if os.path.exists(path):
		return path
	basepath=os.path.basename(path).lower()
	for nearpath in glob.glob(os.path.join(os.path.dirname(path),'*')):
		if os.path.basename(nearpath).lower()==basepath:
			return nearpath


if args.zbmp is None:
	possibles=[args.bmp.rsplit('.',i)[0]+'.zbmp' for i in range(args.bmp.count('.')+1)]
	for path in possibles:
		path=correctPathCase(path)
		if path is not None:
			args.zbmp=path
			break


	if args.zbmp is None:
		print >>sys.stderr,"Couldn't find any ZBMP automatically at any of these locations: %s\nPlease specifiy the path manually!" % ','.join(possibles)
		sys.exit()

template_image=Image.open(args.bmp)

# insert the black and bright green colors into the palette
template_image.palette.palette='\0\0\0\0\0\xFF\0\0'+template_image.palette.palette[8:]

# Ensure imgs exists and it is empty of GIFs
try:
	os.mkdir('imgs')
except OSError:
	pass
for path in glob.glob('imgs/*.gif'):
	os.unlink(path)

frames=[]
with open(args.zbmp,'rb') as f:
	header=f.read(12)
	arr=numpy.fromfile(f, numpy.dtype('<H'))
	view=numpy.reshape(arr, (306,544))
	zmin=auto_zmin=numpy.nanmin(view)
	zmax=auto_zmax=numpy.nanmax(view)
	zmin_extra=zmax_extra=''

	if args.zmin is not None:
		zmin = args.zmin
		zmin_extra = ' (Overridden to {})'.format(zmin)
	if args.zmax is not None:
		zmax = args.zmax
		zmax_extra = ' (Overridden to {})'.format(zmax)


	print """
Automatic zmin = {zmin}{zmin_extra}
Automatic zmax = {zmax}{zmax_extra}""".format(
		zmin=zmin,zmax=zmax, 
		zmin_extra=zmin_extra, zmax_extra=zmax_extra)
	zstep=(zmax-zmin)/args.steps

	last_threshold=0
	last_image = None
	print 'Creating frames'
	frame_range=range(zmin,zmax,zstep)
	if args.reverse:
		frame_range=frame_range[::-1]
	for i,threshold in enumerate(frame_range+[None]):
		im=template_image.copy()
		if threshold is None:
			if args.reverse:
				last_threshold=threshold=-1
			else:
				last_threshold=threshold=65536

		outfile='imgs/%03i-%d.gif' % (i,threshold)
		for (y,x),value in numpy.ndenumerate(view):
			if args.reverse:
				if value<threshold:
					im.putpixel((x,y),0)
				elif value<last_threshold:
					im.putpixel((x,y),1)
			else:
				if value>threshold:
					im.putpixel((x,y),0)
				elif value>last_threshold:
					im.putpixel((x,y),1)

		last_threshold=threshold

		im.save(outfile)
		frames.append(outfile)
		
if not args.skip_gif:
	print 'Creating GIF'
	cmd=['gifsicle','-O','--delay={}'.format(args.speed),'--loop']
	for frame in frames:
		cmd.append(frame)
	if args.last_frame>0:
		cmd.extend(['--delay=200',frames[-1]])
	cmd.extend(['-o',args.output])
	check_call(cmd)
	print 'Done'



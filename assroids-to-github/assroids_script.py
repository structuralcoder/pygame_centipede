#assRoids
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
import pygame,random
from threading import *
from math import *

pygame.init()
print("assRoids initiated")
version='1.0'
#######################################
#PRODUCE A SCREEN
infoObject = pygame.display.Info()
winSize=(infoObject.current_w, infoObject.current_h)
#winSize = (800, 600)
moveMod=1
if infoObject.current_w>winSize[0]:
	moveMod=winSize[0]/infoObject.current_w

screen = pygame.display.set_mode(winSize)
pygame.display.set_caption('assroids')
#######################################################
#######################################################
#######################################################
class img:
	def __init__(self,source):
		self.source=pygame.image.load(source)
		bckrect=self.source.get_rect()
		self.width=bckrect[2]
		self.height=bckrect[3]
		self.offset=[0,0]
		self.pos=[0,0]
		self.size=[self.width,self.height]

#######################################################
#######################################################
class spriteSheet:
	def __init__(self,filename,cols,rows,w,h):
		global WinSize
		self.sheet=pygame.image.load(filename).convert_alpha()
		rect=self.sheet.get_rect()
		
		self.sheet=pygame.transform.scale(self.sheet,(w*cols,h*rows))
		
		
		self.cols=cols
		self.rows=rows
		
		self.totalCellCount=cols*rows
		self.dir=5
		self.CENTER_HANDLE=0
		
		self.rect=self.sheet.get_rect()
		w=self.cellWidth=self.rect.width / cols
		h=self.cellHeight=self.rect.height / rows
		hw,hh=self.cellCenter=(w/2,h/2)
		
		self.cells=list([(self.dir%cols*w,self.dir%rows*h,w,h)for self.dir in range(self.totalCellCount)])
		
		self.handle=list([
			(0,0),(-hw,0),(-w,0),
			(0,-hh),(-hw,-hh),(-w,hh),
			(0,-h),(-hw,-h),(-w,-h)])
		
		#pos on screen
		self.left=(winSize[0]/2)-hw
		self.top=(winSize[1]/2)-hh
		self.right=self.left+w
		self.bottom=self.top+h
		#position on map:
		self.posLeft=(winSize[0]/2)-hw-background.offset[0]+20
		self.posTop=(winSize[1]/2)-hh-background.offset[1]+40
		self.posRight=self.left+w-background.offset[0]-20
		self.posBottom=self.top+h-background.offset[1]-10
			
	def draw(self,surface,cellIndex,x,y,handle=0):
				#blit(source,                    dest,                               area=None,              special_flags = 0) -> Rect#
		surface.blit(self.sheet,(x+self.handle[handle][0],y+self.handle[handle][1]),self.cells[cellIndex])
###################################################################################
###################################################################################
###################################################################################
#img(source)
#bulletTypes='key':'img()',damage,rate,sound,magazine
bulletTypes={
	'blaster':[img('ships/blaster.png'),1,40,pygame.mixer.Sound('sounds/laser1.wav'),5],
	'eblaster':[img('ships/eblaster.png'),1,10,pygame.mixer.Sound('sounds/eblaster.wav')],
	'eshot':[img('ships/partical.png'),1,15,pygame.mixer.Sound('sounds/eshot.wav')],
	'spreader':[img('ships/partical.png'),1,30,pygame.mixer.Sound('sounds/eshot.wav'),2],
	'beam':[img('ships/laserBeam.png'),1,80,pygame.mixer.Sound('sounds/beam.wav'),3],
	'rockets':[img('ships/rocketpic.png'),2,30,pygame.mixer.Sound('sounds/rocket.wav'),3],
}
class bullet:
	def __init__(self,x,y,typ,dir,id):
		global bulletTypes
		self.id=id
		self.x=x
		self.y=y
		self.typ=typ
		self.dir=dir
		self.pic=bulletTypes[typ][0]
		w=self.w=self.pic.width
		h=self.h=self.pic.height
		self.r=w+x
		self.b=y+h
		self.dam=bulletTypes[typ][1]
		self.rate=bulletTypes[typ][2]
		self.spread=0
		self.sub=0
		self.tracking=[x,y]
		
		
upgrades={
	1:['spreader',img('ships/spreader.png')],
	2:['beam',img('ships/beam.png')],
	3:['rockets',img('ships/rockets.png')],
}

pickups=[]

class upgrade:
	def __init__(self,x,y):
		self.x=x
		self.y=y
		self.rate=5
		self.dir=1
		selector=random.randint(1,3)
		self.upgrade=upgrades[selector][0]
		self.pic=upgrades[selector][1].source
		pickups.append(self)
		
###################################################################################
###################################################################################
###################################################################################
ships=[]
enemybullets=[]
id=0
class ship:
	#ship(pic,cols,rows,x,y,w,h,typ,gun)
	def __init__(self,name,pic,cols,rows,x,y,w,h,typ,hp,gun,speed):
		global id
		#spriteSheet(filename,cols,rows)
		self.name=name
		self.id=id
		self.sprite=spriteSheet(pic,cols,rows,w,h)
		self.dir='d'
		self.typ=typ
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		self.r=w+x
		self.b=y+h
		self.hp=hp
		self.fire=0
		self.firemod=1
		self.gun=gun
		self.magazine=5
		self.reload=1
		self.moving=0
		self.moveWait=0
		self.hit=0
		self.die=0
		self.points=1
		self.collision={'left':0,'right':0,'up':0,'down':0}
		self.speed=speed
		self.bullets=[]
		self.continuous=0
		
		ships.append(self)
		#print(ships)
		id+=1
		
	def move(self):
		global winSize
		global moveMod
		if self.moving==1:
			#print(self.name+'.move()')
			#print(self.sprite.dir)
			#move over map:
			if self.moveWait>0:
				#print(str(background.offset[0])+'/'+str(background.offset[1]))
				if self.dir=='d':
					#move down
					if self.collision['down']==0 and self.b<winSize[1]:
						self.y+=self.speed*moveMod
						self.b+=self.speed*moveMod
				elif self.dir=='u':
					#move up
					if self.collision['up']==0 and self.y>=(winSize[1]*.5):
						self.y-=self.speed*moveMod
						self.b-=self.speed*moveMod
				elif self.dir=='r':
					#move right
					if self.collision['right']==0 and self.r<winSize[0]:
						#print('self.x:'+str(self.x))
						#print('self.r:'+str(self.r))
						#print('winSize[0]:'+str(winSize[0]))
						self.x+=self.speed*moveMod
						self.r+=self.speed*moveMod
				elif self.dir=='l':
					#move left
					if self.collision['left']==0 and self.x>0:
						self.x-=self.speed*moveMod
						self.r-=self.speed*moveMod
				
			elif hero.hp>0:
				self.moveWait+=1
	
	def shoot(self):
		if self.name=='hero':
			if self.magazine==0:
				self.gun='blaster'
				self.magazine=5
				self.reload=1
			get_x=self.x
			get_y=self.y
			if len(self.bullets)<self.magazine and self.reload==1:
				bulletTypes[self.gun][3].play()
				bbb=bullet((get_x+(self.w/2)),get_y,self.gun,-1,'hero')
				if self.gun=='beam':
					if len(self.bullets)==0:
						self.bullets.append(bbb)
				else:
					self.bullets.append(bbb)
				if self.gun=='spreader':
					hero.continuous+=1
		
		
		
		else:
			get_x=self.x
			get_y=self.y
			if len(self.bullets)<self.magazine:
				bulletTypes[self.gun][3].play()
				bb=bullet((get_x+(self.w/2)),get_y,self.gun,1,self.id)
				self.bullets.append(bb)
				enemybullets.append(bb)
				
			
###################################################################################
###################################################################################

background=img('ships/space2.png')
background.source=pygame.transform.scale(background.source,(winSize))
bckrect=background.source.get_rect()
background.size=[background.width,background.height]

#ship(name,pic,cols,rows,x,y,w,h,typ,gun,speed)
score=0
#score=19
def setupHero():
	global hero
	hero=ship('hero','ships/awing.png',1,1,0,0,40,50,'personal',10,'blaster',15)
	hero.x=(winSize[0]/2)-(hero.w/2)
	hero.r+=hero.x
	hero.y=((winSize[1]/4)*3)-(hero.h/2)
	hero.b+=hero.y
	hero.id='hero'
	hero.fire=1
	#hero.hp=1
	#hero.gun='beam'
setupHero()

explodepic=pygame.image.load('ships/explode.png')
splosion=pygame.mixer.Sound('sounds/splosion.wav')
heroDie=pygame.mixer.Sound('sounds/heroDie.wav')
class explode:
	global explodepic
	def __init__(self,x,y,w):
		self.pic=pygame.transform.scale(explodepic,(w,w))
		self.x=x
		self.y=y
		self.w=w
		splosion.play()
	def destroy(self):
		self.x=self.x-(self.w/3)
		self.r=self.x+self.w
		self.b=self.y+self.w
		for s in ships:
			if s.name!='hero':
				if s.b>=self.y and s.y<=self.b:
					if s.x<=self.r and s.r>=self.x:
						s.hp-=2
		
		
explosions=[]

def checkCollision():
	global explode
	global ships
	global enemybullets
	global score
	global songlist
	
	for b in hero.bullets:
		breaker=0
		for t in ships:
			if t.name!='hero' and breaker!=1:
				if b.y<=t.b and b.b>t.y:
					if t.r>=b.x and t.x<=b.r:
						t.hp-=b.dam
						if b.typ!='beam':
							hero.bullets.remove(b)
						if b.typ=='rockets':
							xx=explode(b.x,b.y,b.h+50)
							explosions.append(xx)
							xx.destroy()
							rmv=Timer(.75,removeExplosion,[xx])
							rmv.start()
						breaker=1
						
			if t.hp<=0:
				xx=explode(t.x,t.y,t.h)
				explosions.append(xx)
				ships.remove(t)
				rmv=Timer(.5,removeExplosion,[xx])
				rmv.start()
				score+=1
				if score%10==0:
					upgrade(t.x,t.y)
	
	for b in enemybullets:
		if b.b>=hero.y and b.y<hero.b:
			if hero.r>=b.x and hero.x<=b.r:
				hero.hp-=b.dam
				enemybullets.remove(b)
			if hero.hp<=0:
				hero.moveWait=0
				xx=explode(hero.x,hero.y,hero.h)
				explosions.append(xx)
				heroDie.play()
	
	for b in subbullets:
		if b.id=='hero':
			for s in ships:
				if s.name!='hero':
					if b.y<=s.b and b.x>=s.x and b.x<s.r:
						s.hp-=1
					if hero.hp<=0:
						s.moveWait=0
						xx=explode(s.x,s.y,s.h)
						explosions.append(xx)
						ships.remove(s)
						rmv=Timer(.5,removeExplosion,[xx])
						rmv.start()
						score+=1
						if score%10==0:
							upgrade(t.x,t.y)
		elif b.id!='hero' and b.b>=hero.y and b.y<hero.b:
			if hero.r>=b.x and hero.x<=b.r:
				hero.hp-=b.dam
				for b2 in enemybullets:
					if b2.id==b.id:
						enemybullets.remove(b2)
				for s in ships:
					if s.id==b.id:
						s.bullets.pop()
			if hero.hp<=0:
				hero.moveWait=0
				xx=explode(hero.x,hero.y,hero.h)
				explosions.append(xx)
	for u in pickups:
		wd=u.pic.get_width()
		ht=u.pic.get_height()
		if (u.y+ht)>hero.y and u.y<hero.b:
			if u.x>hero.x and u.x<hero.r:
				hero.gun=u.upgrade
				hero.continuous=0
				hero.magazine=bulletTypes[u.upgrade][4]
				#print('hero gun changed to: '+u.upgrade)
				pickups.remove(u)
			elif (u.x+wd)<hero.r and (u.x+wd)>hero.x:
				hero.gun=u.upgrade
				hero.continuous=0
				hero.magazine=bulletTypes[u.upgrade][4]
				#print('hero gun changed to: '+u.upgrade)
				pickups.remove(u)
	for s in ships:
		if s.name!='hero':
			if s.hp<=0:
				xx=explode(s.x,s.y,s.h)
				explosions.append(xx)
				ships.remove(s)
				rmv=Timer(.5,removeExplosion,[xx])
				rmv.start()
				score+=1
				if score%20==0:
					upgrade(s.x,s.y)
	if hero.hp<=0:
		changeSong(songlist['sPACE'])

def removeExplosion(e):
	global explosions
	explosions.remove(e)
	
initials=[
	[0,(64, 252, 43)],
	[0,(64, 252, 43)],
	[0,(64, 252, 43)]
]
alphabet=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','!','@','#','$','%','^','&','*','(',')','-','+','=','_','`','~']

initIndex=0
def endRound():
	global win
	global initials
	global alphabet
	global songlist
	global initIndex
	initFont=pygame.font.SysFont('Arial', int(winSize[1]/4))
	
	
	for i in initials:
		i[1]=(64, 252, 43)
	initials[initIndex][1]=(0,100,255)
	
	win=1
	
	initBoxX=winSize[0]/4
	initBoxW=winSize[0]/2
	initBoxY=winSize[1]/4
	initBoxH=winSize[1]/2
	
	pygame.draw.rect(screen,(82,82,82),(initBoxX,initBoxY,initBoxW,initBoxH))
	e=0
	for i in initials:
		printInit=initFont.render(alphabet[i[0]], False, i[1])
		get_width=(printInit.get_width()+30)
		whole_width=get_width*3
		get_height=(printInit.get_height())
		setX=((initBoxW-whole_width)/2)+(get_width*e)+initBoxX
		setY=((initBoxH-get_height)/2)+initBoxY
		screen.blit(printInit,(setX,setY))
		e+=1
		
def changeInitials(index,move):
	global initials
	global alphabet
	initials[index][0]+=move
	if initials[index][0]>(len(alphabet)-1):
		initials[index][0]=0
	if initials[index][0]<0:
		initials[index][0]=len(alphabet)-1
	endRound()
	
	
	
###################################################################################
#shipNumbers=pygame.font.SysFont('Arial', 60)
def showShips():
	#global shipNumbers
	global screen
	for s in ships:
		screen.blit(s.sprite.sheet,(s.x,s.y))
		#idid=shipNumbers.render(str(s.id),False,(78, 245, 66))
		#screen.blit(idid,(s.x,s.y))
	for x in explosions:
		screen.blit(x.pic,(x.x,x.y))
subbullets=[]
def showBullets():
	global screen
	global winSize
	global subbullets
	subbullets.clear()
	for b in hero.bullets:
		screen.blit(b.pic.source,(b.x,b.y))
		b.y=b.y+((b.rate*b.dir)*moveMod)
		b.b=b.b+((b.rate*b.dir)*moveMod)
		
		if b.typ=='beam' and hero.magazine>0:
			b.b=hero.y
			if b.y<=0:
				b.y=0
			heroCntr=((hero.r-hero.x)/2)+hero.x
			beamHW=(b.r-b.x)/2
			b.x=heroCntr-beamHW
			b.r=b.x+(beamHW*2)
			beamH=hero.y-b.y
			beamW=b.pic.source.get_width()
			#print(beamW)
			b.pic.source=pygame.transform.scale(b.pic.source,(beamW,int(beamH)))
		
		elif b.typ=='rockets':
			#               0      1
			#tracking==[start_x,start_y]
			distance=b.tracking[1]-b.y
			#print(distance)
			if distance>=600:
				xx=explode(b.x,b.y,b.h+50)
				explosions.append(xx)
				xx.destroy()
				rmv=Timer(.75,removeExplosion,[xx])
				rmv.start()
				hero.bullets.remove(b)
				hero.magazine-=1
			
		elif b.typ=='spreader' and hero.continuous<8:
			b.spread+=8
			b.x-=4
			b.r-=4
			chain=b.spread/4
			#bullet(x,y,typ,dir,id)
			i=0
			while i < 4:
				subbullets.append(bullet((b.x+(chain*i)),b.y+(b.rate*moveMod),'spreader',-1,b.id))
				i+=1
		elif b.typ=='spreader' and hero.continuous>=8:
			hero.gun='blaster'
			hero.magazine=0
			hero.continuous=0
		
		
		if b.b<=0 or b.y>winSize[1]:
			#print(s.name)
			hero.bullets.remove(b)
		elif b.typ=='beam' and b.y<=0:
			b.y=0
			hero.reload=0
			#print(hero.continuous)
			if hero.continuous<30:
				hero.continuous+=1
			else:
				hero.bullets.remove(b)
				hero.continuous=0
				hero.reload=1
				hero.magazine-=1
			
	for b in enemybullets:
		screen.blit(b.pic.source,(b.x,b.y))
		b.y=b.y+((b.rate*b.dir)*moveMod)
		b.b=b.b+((b.rate*b.dir)*moveMod)
		
		if b.typ=='eshot':
			b.spread+=8
			b.x-=4
			b.r-=4
			chain=b.spread/4
			#bullet(x,y,typ,dir,id)
			i=0
			while i < 4:
				subbullets.append(bullet((b.x+(chain*i)),b.y,'eshot',1,b.id))
				i+=1
			
			
		if b.b<=0 or b.y>winSize[1]:
			#print(s.name)
			enemybullets.remove(b)
			for s in ships:
				if s.id==b.id:
					s.bullets.pop()
	
	for b in subbullets:
		screen.blit(b.pic.source,(b.x,b.y))
	
	for u in pickups:
		screen.blit(u.pic,(u.x,u.y))
		u.y+=(u.rate*u.dir)*moveMod
	
	checkCollision()
###################################################################################
###################################################################################
###################################################################################
enemies={
	#'key' : [  source,        c,r, w, h,hp,gun,   speed,magazine,fireMod,WavePoints]
	#				0		   1 2 3  4  5    6       7 8 9 10
	'drone':['ships/drone.png',1,1,40,60,1,'eblaster',5,1,1,1],
	'slicer':['ships/slicer.png',1,1,80,60,2,'eblaster',5,3,50,2],
	'shotgun':['ships/shotgun.png',1,1,80,60,2,'eshot',5,1,20,3],
}
enemyList=[]
for k in enemies.keys():
	enemyList.append(k)
waveClear=0
wave=0
waveWait=0
def getWave():
	#print('getWave')
	global wave
	global waveClear
	global waves
	global winFont
	global menuFont
	global win
	global enemyList
	global enemies
	offset=0
	offsetv=0
	if waveClear==1:
		waveClear=0
		list=[]
		wavePoints=(wave*10)+5
		usedPoints=0
		while usedPoints<wavePoints:
			ran=random.randint(0,(len(enemies)-1))
			randomName=enemyList[ran]
			points=enemies[randomName][10]
			if usedPoints<=points:
				usedPoints+=points
				list.append(randomName)
			else:
				list.append('drone')
				usedPoints+=1
		wave+=1
		z=0
		for n in list:
			zone=winSize[0]/4
			shift=offset*enemies[n][3]
			shiftv=0
			if (offset%3)>0:
				shiftv=enemies[n][4]*offsetv
			else:
				offsetv+=1
			#enemies={'key':source,cols,rows,hp,dam,gun}
			#ship(pic,cols,rows,x,y,w,h,typ,gun,firemod)
			ship(n,enemies[n][0],enemies[n][1],enemies[n][2],(zone*z)+shift,(0-enemies[n][4])-shiftv,enemies[n][3],enemies[n][4],'enemy',enemies[n][5],enemies[n][6],enemies[n][7])
			z+=1
			if z>=4:
				offset+=1
				z=0
		for s in ships:
			if s.name!='hero':
				s.dir=3
				s.changeWait=0
				s.changeVert=0
				s.fireWait=0
				s.fall=0
				s.magazine=enemies[s.name][8]
				s.fireMod=enemies[s.name][9]
				if s.x>=(winSize[0]/2):
					s.dir=4
	

			

rails={
	'drone':'slide'
}	
def moveWave():
	global winSize
	global enemies
	global moveMod
	scatter=0
	for s in ships:
		if s.x>winSize[1]:
			scatter+=1
		if s.name!='hero':
					#    0      1      2      3
			#directions=['up','down','left','right']
			#dir=random.randint(0,3)
			if s.y<=0:
				s.y+=s.speed*moveMod;s.b+=s.speed*moveMod
			
			changeDir=random.randint(1,100)
			#change dir
			if changeDir>=70 and s.changeWait>300:
				#print('changeDir')
				s.changeWait=0
				if s.dir==3:
					s.dir=2
				if s.dir==2:
					s.dir=3
				if scatter>=(len(ships)/2):
					s.dir=2
			#change vert
			if s.changeVert>100 and s.y>0:
				s.changeVert=0
				s.fall=random.randint(-1,1)
				
					
					
			
			if s.dir==3 and s.r<(winSize[0]-5):
				s.x+=s.speed*moveMod;s.r+=s.speed*moveMod;	
			else:
				s.dir=2
			if s.dir==2 and s.x>5:
				s.x-=s.speed*moveMod;s.r-=s.speed*moveMod;	
			else:
				s.dir=3
			#move vertically	
			if s.fall>0 and s.y<((winSize[1]*.45)-s.h):
				s.y+=s.speed*moveMod;s.b+=s.speed*moveMod;
			elif s.fall<0 and s.y>0:
				s.y-=s.speed*moveMod;s.b-=s.speed*moveMod;
			
			#fire:
			fireChance=random.randint(1,10000)
			if (fireChance*enemies[s.name][9])>9900 and (s.fireWait+enemies[s.name][9]-1)>50 and s.y>=0:
				s.fireWait=0
				s.shoot()
					
				
			
			s.changeWait+=1
			s.changeVert+=1
			if len(s.bullets)<s.magazine:
				s.fireWait+=1

###################################################################################
###################################################################################
selectAShip=[
	#spriteSheet(pic,cols,rows,w,h)
	['awing',spriteSheet('ships/awing.png',1,1,40,50)],
	['ywing',spriteSheet('ships/ywing.png',1,1,40,50)],
	['xwing',spriteSheet('ships/xwing.png',1,1,40,50)],
	['blueStreak',spriteSheet('ships/blueStreak.png',1,1,40,50)],
	['catExtreme',spriteSheet('ships/catExtreme.png',1,1,40,50)],
	['f22',spriteSheet('ships/f22.png',1,1,40,50)],
	['dragon',spriteSheet('ships/dragon.png',1,1,80,39)],
	['8bitMerica',spriteSheet('ships/8bitMerica.png',1,1,40,50)],
	#['sr71',spriteSheet('ships/sr71.png',1,1,40,50)],
	['fireFly',spriteSheet('ships/fireFly.png',1,1,40,50)],
	['FTL1',spriteSheet('ships/FTL1.png',1,1,40,50)],
	#['FTL2',spriteSheet('ships/FTL2.png',1,1,40,50)],
	['millionth',spriteSheet('ships/millionth.png',1,1,40,50)],
	#['razor1',spriteSheet('ships/razor1.png',1,1,40,50)],
	#['talon1',spriteSheet('ships/talon1.png',1,1,40,50)],
	
]


class menu:
	def __init__(self):
		global version
		self.ship=0
		self.background='space2'
		self.version=version
		self.menu=[]
		self.selector=0
		self.base=0
		self.rows=0
		self.cols=0
		self.keybounce=0
		
		self.v_opacity=0
		self.m_opacity=0
		self.s_opacity=[]
	
	def returnMenuSelect(self,sel):
		global selectAShip
		global lockin
		global history
		global menuFont
		#print(sel)
		if self.base==0:
			if sel==0:
				#SELECT A SHIP
				self.base=1
				self.menu=[]
				self.shipSelectionWidth=0
				for s in selectAShip:
					self.menu.append(s[1])
					self.shipSelectionWidth+=140
					if self.shipSelectionWidth>(winSize[0]-300):
						self.shipSelectionWidth-=140
			if sel==1:
				self.base=2
				self.selector=0
				self.menu=[]
				for h in history:
					h=h.replace('\n','')
					H=menuFont.render(h, False, (64, 252, 43))
					self.menu.append(H)
				if not self.menu:
					self.menu.append(winFont.render('NO SCORES RECORDED', False, (64, 252, 43)))
			if sel==2:
				self.base='x'
				self.menu=[]
				controllesFont=pygame.font.SysFont('Arial', int(winSize[1]*.04))	
				self.menu=[
					pygame.image.load('ships/keyboard.png'),
					controllesFont.render('W: MOVE UP', False, (64, 252, 43)),
					controllesFont.render('S: MOVE DOWN', False, (64, 252, 43)),
					controllesFont.render('A: MOVE LEFT', False, (64, 252, 43)),
					controllesFont.render('D: MOVE RIGHT', False, (64, 252, 43)),
					controllesFont.render('-OR-', False, (64, 252, 43)),
					controllesFont.render('↑: SQUANCH UP', False, (64, 252, 43)),
					controllesFont.render('↓: SQUANCH DOWN', False, (64, 252, 43)),
					controllesFont.render('←: SQUANCH LEFT', False, (64, 252, 43)),
					controllesFont.render('→: SQUANCH RIGHT', False, (64, 252, 43)),
					controllesFont.render('SPACEBAR: SELECT/FIRE/GO BACK', False, (64, 252, 43)),
					controllesFont.render('-OR-', False, (64, 252, 43)),
					controllesFont.render('ENTER: SELECT A SQUANCH/SQUANCH A FOOL/', False, (64, 252, 43)),
					controllesFont.render('                    BACK A SQUANCH', False, (64, 252, 43)),
					controllesFont.render('                    ', False, (64, 252, 43)),
					controllesFont.render('Back Space: GO BACK', False, (64, 252, 43)),
					controllesFont.render('                    ', False, (64, 252, 43)),
					controllesFont.render('ESC: CLOSE GAME', False, (64, 252, 43)),
				]
				kbw=self.menu[0].get_width()
				kbh=self.menu[0].get_height()
				newW=winSize[0]*.9
				percDiff=newW/kbw
				newH=kbh*percDiff
				
				self.menu[0]=pygame.transform.scale(self.menu[0],(int(newW),int(newH)))
				
				self.base=3
				self.selector=0
				
		elif self.base==1:
			#change ship
			hero.sprite=selectAShip[self.selector][1]
			#start game
			lockin=1
			changeSong(songlist['gamesong'])
		
		elif self.base==2:
			self.goBackToBase()
		elif self.base==3:
			self.goBackToBase()
		
	def setToZero(self):
		global win
		global lockin
		global hero
		global title
		global songlist
		global score
		global menuFont
		
		ships.clear()
		setupHero()
		
		score=0
		getHistory()
		self.menu.clear()
		self.menu=[
			menuFont.render('START', False, (64, 252, 43)),
			menuFont.render('SCORES', False, (64, 252, 43)),
			menuFont.render('CONTROLLES', False, (64, 252, 43))
		]
		changeSong(songlist['titlesong'])
		lockin=0
		win=0
		title.base=0
		title.selector=0
		
	def goBackToBase(self):
		global menuFont
		getHistory()
		self.menu.clear()
		self.menu=[
			menuFont.render('START', False, (64, 252, 43)),
			menuFont.render('SCORES', False, (64, 252, 43)),
			menuFont.render('CONTROLLES', False, (64, 252, 43))
		]
		lockin=0
		win=0
		hero.hp=10
		title.base=0
		title.selector=0
###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################
running=True
waveWait=0
		
statfont = pygame.font.SysFont('Arial', 40)	
winFont = pygame.font.SysFont('Arial', 80)	
menuFont = pygame.font.SysFont('Arial', int(winSize[1]*.05))

win=0
winText=winFont.render('STAGE COMPLETE!!',False,(78, 245, 66))
winText_width = winText.get_width()
winText_height = winText.get_height()


lockin=0
title=menu()
titleStart=0

songlist={
'gamesong':'music/stress.mp3',
'titlesong':'music/shortTrance.wav',
'sPACE':'music/sPACE.mp3',
}
def playsong():
	pygame.mixer.music.play(-1)

def changeSong(file):
	pygame.mixer.music.load(file)
	playsong()

changeSong(songlist['titlesong'])



COMMENTS=0
creatorComments=[
'TO WIN THE GAME, BEAT THE HIGH SCORE, DONT BE LIKE RANDAL',
'THIS GAME FEATURES ENDLESS WAVES, RANDAL DIDNT MAKE IT #2',
'ROCKETS TRAVEL A CERTAIN DISTANCE BEFORE EXPLODING',
'THE ION BEAM ONLY HAS THREE SHOTS, BUT WILL FOLLOW YOUR SHIP',
'THE SHOTGUN CAN BE FIRED TWO TIMES VERY QUICKLY',
'I TRIED TO EXPLAIN THIS SYSTEM TO RANDAL, BUT HE WAS DISTRACTED',
'"THE GOAL IS TO AVOID THE RED ENEMY BULLETS, RANDAL", I TOLD HIM',
'BUT YOU CANT BLAIM HIM, HIS DOG GOT RAN OVER LAST MONTH',
'RANDAL REALLY LIKED HIS DOG',
'RANDAL REALLY, REALLY LIKED HIS DOG',
'IT WAS THE ONLY FAMILY HE HAD LEFT AFTER HIS MOM AND DAD SEPERATED',
'I TOLD HIM, "JUST PLAY ASSROIDS, THATLL TAKE YOUR MIND OF LUCKY"',
'BUT AFTER RANDALS MISERABLE FAILURE, HE JUST STARTED SOBBING',
'"HE WASNT THAT LUCKY...", HE SAID OVER AND OVER',
'IN MY HEAD I WAS LIKE: "OH GO CRY ABOUT IT ON FACEBOOK"',
'BUT INSTEAD I SAID, "HERE RANDAL, PICK ANOTHER SHIP FROM THE MENU"',
'WELL THAT REALLY SET HIM OFF...',
'HE WAS HAVING TROUBLE SEEING ALL THE FINE SHIP DESIGNS THROUGH THE TEARS',
'THE CHOICES PROVED TOO DAUGHNTING FOR HIM, AT THE MOMENT',
'YOU GOT TO REMEMBER, WHEN THE BLASTER IS ON THE RIGHT, GO LEFT',
'THE GRAY ONES ARE DRONES, THE TRIPLE SHOTS ARE SLICERS',
'THE BIG "U" SHIP HAS A SHOTGUN BLAST, YES WE SEE THE BUG',
'"WHY THE HELL ARE THEY SHAPED LIKE A "U" THEN?", RANDAL EXPLAIMED',
'"I DONT KNOW, I STOLE IT OFF THE INTERNET REAL QUICK", SAYS I',
'WELL THAT WASNT GOOD ENOUGH FOR RANDAL',
'HIM GO RUNNIN OUT THE OFFICE LIKE A CRAZED BULL ELEPHANT',
'NO ONES SEEN RANDAL SINCE,',
'ASSROIDS WAS STILL IN DEVELOPMENT THEN,',
'SO THAT MEANS RANDAL MISSED OUT ON "CONTROLLES" MENU',
'THAT PLUS THESE COMMENTS WOULD HAVE REALLY HELPED THE CRAZED BASTARD',
'JUST COME ON BACK IF YOU NEED ANY MORE INFORMATION ON ASSTROIDS',
'NEW VERSIONS MAY CONSIST OF NEW SHIPS AND POSSIBLY OPTIONS',
'MY LAWYER SAYS IM NOT TO SAY ANYTHING ELSE ABOUT THE RANDAL CASE',
'...SO DONT ASK',
'"THANKS FOR PLAYING MY GAME"',
]


shipshift=0
ScrollMod=0
def HERTZ():
	global waveWait
	global waveClear
	global statfont
	global winText
	global winText_width
	global titleStart
	global COMMENTS
	global creatorComments
	global win
	global ScrollMod
	global shipshift
	if running:
		if win==0 and lockin==1:
			if len(ships)==1:
				waveClear=1
				waveWait+=1
			
			if hero.moving==1:
				hero.move()
			
			
			if waveWait==100:
				waveWait=0
				getWave()
			if hero.hp>0:
				screen.fill((0,0,0))
				screen.blit(background.source,background.offset)
				moveWave()
				showBullets()
				showShips()
				stats = statfont.render(str(hero.hp)+'/10  SPLODED: '+str(score)+' WAVE: '+str(wave), False, (64, 252, 43))
				screen.blit(stats,(0,winSize[1]-50))
			
			if hero.hp<=0 and hero.hp>-800:
				hero.hp-=1
				#print(hero.hp)
			if hero.hp<=-800:
				endRound()
			
			
		
	
	
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		elif lockin==0:
			#print('Game Start, Title Screen')
			titleFont=pygame.font.SysFont('Arial', int(winSize[1]/4))
			
			titleName = titleFont.render('ASSROIDS', False, (64, 252, 43))
			title_width = titleName.get_width()
			screen.blit(background.source,(0,0))
			screen.blit(titleName,((winSize[0]/2)-(title_width/2),20))
			
			titleStart+=10
			if titleStart>100:
				titleStart=100
			opacity=titleStart*5
			if opacity>255:
				opacity=255
			title.v_opacity=opacity
			if opacity==255:
				title.m_opacity+=5
				if title.m_opacity>=255:
					title.m_opacity=255
			versionNumber = winFont.render('v'+title.version, False, (64, 252, 43))
			versionNumber.set_alpha(title.v_opacity)
			screen.blit(versionNumber,((winSize[0]/2)-(title_width/2),int(winSize[1]/4)+30))
			
			###########									################
			
			if title.base==1:
				i=0
				e=0
				sss=0
				selectionWidth=title.shipSelectionWidth-40
				startX=(winSize[0]/2)-(selectionWidth/2)
				title.rows=0
				
				#print(title.selector)
				for s in title.menu:
					placeX=startX+(140*i)
					squareColor=(82,82,82)
					if sss==title.selector:
						squareColor=(0,100,255)
						shipOnScreen=winSize[1]*.6+e
					pygame.draw.rect(screen, squareColor,(placeX,winSize[1]*.6+e-shipshift,100,100))
					
					shipPicW=s.sheet.get_width()/2
					shipPicH=s.sheet.get_height()/2
					xxx=placeX+50-shipPicW
					yyy=(winSize[1]*.6+e)+50-shipPicH
					screen.blit(s.sheet,(xxx,yyy-shipshift))
					
					i+=1
					sss+=1
					if winSize[0]-(placeX+140)<300:
						title.cols=i-1
						title.rows+=1
						e+=140
						i=0
				
				
				#show comments
				txt=creatorComments[COMMENTS]
				txt=statfont.render(txt,False,(64, 252, 43))
				txtW=txt.get_width()
				txtH=txt.get_height()
				xxx=(winSize[0]-txtW)/2
				commentBoxColor=(75,75,75)
				if title.selector=='cc':
					commentBoxColor=(0,100,255)
				pygame.draw.rect(screen, commentBoxColor,(xxx-30,(winSize[1]*.5)-txtH-30,txtW+60,txtH+60))
				
				screen.blit(txt,(xxx,(winSize[1]*.5)-txtH))
				
				arrow_left=winFont.render('◄', False, (64, 252, 43))
				arrow_right=winFont.render('►', False, (64, 252, 43))
				arrW=arrow_left.get_width()
				arrH=arrow_left.get_height()
				Vcntr=((txtH+60)-(arrH))/2
				bxTop=(winSize[1]*.5)-txtH-30
				setY=bxTop+Vcntr
				setSecondX=(xxx)+txtW+10
				#(winSize[1]*.5)-30-txtH-Vcntr)
				
				screen.blit(arrow_left,(xxx-arrW,setY))
				screen.blit(arrow_right,(setSecondX,setY))
			
			################							################
			
			elif title.base==0 or title.base==2:
				if titleStart==20:
					title.setToZero()
				
				if title.base==0:
					ScrollMod=0
				
				totalH=0
				i=0
				title.s_opacity=[]
				SCROLLRESET=0
				for m in title.menu:
					title.cols=0
					title.rows+=1
					optionwidth=m.get_width()
					optionheight=m.get_height()
					totalH+=optionheight
					m.set_alpha(title.m_opacity)
					SCROLLCHECK=int(winSize[1]*.6)+(optionheight*i)-ScrollMod
					if SCROLLCHECK>=int(winSize[1]*.6):
						screen.blit(m,((winSize[0]/2)-(optionwidth/2),SCROLLCHECK))
						SCROLLRESET+=1
					#title.s_opacity.append([opacity,x,y])
					#title.s_opacity.append([  0     1 2])
					title.s_opacity.append([0,(winSize[0]/2)-(optionwidth/2)-80,int(winSize[1]*.6)+(optionheight*i)])
					i+=1
					#print('title.s_opacity: '+str(title.s_opacity))
				
				if SCROLLRESET==0:
					title.goBackToBase()
					
				if title.m_opacity==250:
					title.selector=0
				if title.m_opacity>=250:
					#print(title.s_opacity)
					title.s_opacity[title.selector][0]=255
					if title.base==0:
						for s in title.s_opacity:
							selector = menuFont.render('►', False, (64, 252, 43))
							selector.set_alpha(s[0])
							screen.blit(selector,(s[1],s[2]))
				
				if title.base==2:
					if (int(winSize[1]*.6))+(totalH)>winSize[1]:
						ScrollMod+=8
					
			
			elif title.base==3:
				#open controlles
				kbw=title.menu[0].get_width()
				setX=(winSize[0]-kbw)/2
				screen.blit(title.menu[0],(setX,0))
				textH=title.menu[1].get_height()
				i=1
				while i<len(title.menu):
					if i<10:
						setY=(winSize[1]*.55)+(textH*(i-1))
						screen.blit(title.menu[i],((winSize[0]*.25),setY))
					else:
						setY=(winSize[1]*.55)+(textH*(i-10))
						screen.blit(title.menu[i],((winSize[0]*.5),setY))
					i+=1
				
				
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
	
	else:
		pygame.quit()
		quit()
	
	pygame.display.update()
####################################################################
####################################################################
history=[]
def getHistory():
	history.clear()
	get_scores=open('scores.txt')
	if get_scores:
		for line in get_scores:
			history.append(line)
	get_scores.close()

def save(currinitials,currscore):
	print('save')
	scoreRegistered=0
	lines=''
	scoresOnBoard=0
	for sc in history:
		sc=sc.replace('\n','')
		sc=sc.split('--')
		if scoreRegistered==0:
			if currscore>int(sc[1]):
				scoreRegistered=1
				lines=lines+alphabet[currinitials[0][0]]+alphabet[currinitials[1][0]]+alphabet[currinitials[2][0]]+'--'+str(currscore)+'\n'
				scoresOnBoard+=1
		if scoresOnBoard<11:
			lines=lines+sc[0]+'--'+sc[1]+'\n'
		
		scoresOnBoard+=1
	if scoresOnBoard<11 and scoreRegistered==0:
		lines=lines+alphabet[currinitials[0][0]]+alphabet[currinitials[1][0]]+alphabet[currinitials[2][0]]+'--'+str(currscore)+'\n'
				
	if lines=='':
		lines=lines+alphabet[currinitials[0][0]]+alphabet[currinitials[1][0]]+alphabet[currinitials[2][0]]+'--'+str(currscore)+'\n'
		
	save_scores=open('scores.txt','w+')
	save_scores.writelines(lines)
	save_scores.close()
	
	
####################################################################
####################################################################
hertz=0
ENTER=0





class sounds:
	def __init__(self):
		self.laser=pygame.mixer.Sound('sounds/laser1.wav')

effects=sounds()

keypress={
	'13':False,
	'27':False,
	'32':False,
	'274':False,
	'273':False,
	'276':False,
	'275':False,
	'119':False,
	'115':False,
	'97':False,
	'100':False,
	'8':False,
}
while running:
	#print(running)
	for event in pygame.event.get():
		#print(event.type)
		
		if event.type==12:
			running=False
			print("GAME QUIT")
			pygame.display.quit()
			pygame.quit()
		if event.type==2:
			keypress[str(event.key)]=True
			if event.key==27:
				#ESC
				running=False
				print("GAME QUIT")
				pygame.display.quit()
				pygame.quit()
				
			#print("key #"+ str(event.key) + " pressed")
			
			if event.key==32 or event.key==13:
				#spaceBar
				if win==0:
					if hero.fire==1 and lockin==1:
						hero.shoot()
					elif lockin==0:
						#print('select menu item')
						kb=Timer(.25,title.returnMenuSelect,[title.selector])
						kb.start()
				elif win==1:
					#print('input initials')
					save(initials,score)
					title.setToZero()
			
			elif event.key==8 and lockin==0:
				title.goBackToBase()
			
			elif event.key==274 or event.key==115:
				#down
				if win==0:
					if lockin==1:
						hero.dir='d'
						hero.moving=1
					elif lockin==0:
						if title.base==0:
							#print('move selector down')
							title.selector+=1
							if title.selector>=len(title.menu):
								title.selector=0
						
						elif title.base==1:
							if title.selector=='cc':
								title.selector=-1
							title.selector+=title.cols+1
							if title.selector>len(title.menu):
								title.selector-=title.cols+1
				elif win==1:
					#print('alphabet down')
					changeInitials(initIndex,-1)
			elif event.key==273 or event.key==119:
				#up
				if win==0:
					if lockin==1:
						hero.dir='u'
						hero.moving=1
					elif lockin==0:
						if title.base==0:
							#print('move selector up')
							title.selector-=1
							if title.selector<0:
								title.selector=len(title.menu)-1
						elif title.base==1:
							if title.selector!='cc':
								title.selector-=title.cols+1
								if title.selector<0:
									title.selector='cc'
									#print('title.selector to cc')
				elif win==1:
					#print('alphabet up')
					changeInitials(initIndex,1)
					
			elif event.key==276 or event.key==97:
				#left
				if win==0:
					if lockin==1:
						hero.dir='l'
						hero.moving=1
					elif lockin==0:
						if title.base==1:
							if title.selector=='cc':
								COMMENTS-=1
								if COMMENTS<0:
									COMMENTS=0
							else:
								title.selector-=1
								if title.selector<0:
									title.selector=len(title.menu)-1
				elif win==1:
					#print('shift: initials left')
					initIndex-=1
					if initIndex<0:
						initIndex=0
					changeInitials(initIndex,0)
			elif event.key==275 or event.key==100:
				#right
				keypress[event.key]=True
				if win==0:
					if lockin==1:
						hero.dir='r'
						hero.moving=1
					elif lockin==0:
						if title.base==1:
							if title.selector=='cc':
								COMMENTS+=1
								if COMMENTS>(len(creatorComments)-1):
									COMMENTS=len(creatorComments)-1
							else:
								title.selector+=1
								if title.selector>(len(title.menu)-1):
									title.selector=0
				elif win==1:
					#print('shift: initials right')
					initIndex+=1
					if initIndex>2:
						initIndex=2
					changeInitials(initIndex,0)
			
		elif event.type==3:
			keypress[str(event.key)]=False
			if event.key==13:
				#enter
				ENTER=0
			
		if keypress['273']==False and keypress['274']==False and keypress['275']==False and keypress['276']==False and keypress['119']==False and keypress['115']==False and keypress['97']==False and keypress['100']==False:
			hero.moving=0
	
	if hertz==1000:
		hertz=0
		HERTZ()
		
		
		
	hertz+=1








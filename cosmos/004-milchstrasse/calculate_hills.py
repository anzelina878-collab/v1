import numpy as np,json,pathlib
# Dimensionless illustrative Newtonian three-body encounter. Central mass held fixed;
# stellar mutual gravity retained. Search phase giving one bound and one unbound component.
M=50.;r=np.array([-15.,7.,0.]);rn=np.linalg.norm(r);er=r/rn;et=np.array([-er[1],er[0],0.]);rp=2.;vt=(2*M*rp)**.5/rn;vr=-(2*M/rn-vt*vt)**.5;v=vr*er+vt*et
for phase in np.arange(0,6.3,.35):
 d=np.array([np.cos(phase),np.sin(phase),0.]);w=np.array([-np.sin(phase),np.cos(phase),0.]);a=r+d*.5;b=r-d*.5;va=v+w*.5;vb=v-w*.5;aa=[];bb=[];dt=.002
 def acc(a,b):
  delta=b-a;coupling=delta/max(np.linalg.norm(delta),.01)**3*.5
  return -M*a/max(np.linalg.norm(a),.05)**3+coupling,-M*b/max(np.linalg.norm(b),.05)**3-coupling
 for i in range(10500):
  fa,fb=acc(a,b);va+=fa*dt/2;vb+=fb*dt/2;a+=va*dt;b+=vb*dt;fa,fb=acc(a,b);va+=fa*dt/2;vb+=fb*dt/2
  if i%36==0:aa.append(a.tolist());bb.append(b.tolist())
 ea=np.dot(va,va)/2-M/np.linalg.norm(a);eb=np.dot(vb,vb)/2-M/np.linalg.norm(b)
 if ea*eb<0 and max(ea,eb)>.3:
  if ea<0:aa,bb=bb,aa;ea,eb=eb,ea
  pathlib.Path('hills-trajectories.json').write_text(json.dumps({'a':aa,'b':bb,'ejection_energy':ea,'capture_energy':eb,'note':'Dimensionless educational three-body illustration; not fitted trajectory of S5-HVS1.'},indent=2));print('Unbound',ea,'Bound',eb,'phase',phase);break
else:raise RuntimeError('No separated encounter found')

cd ~/autonomous-mower/cad
for mod in PRINT_equipment_plate PRINT_upper_shelf; do
  MZ=$(python3 -c "
mn=1e9
for l in open('stl/$mod.stl'):
 s=l.split()
 if len(s)>=4 and s[0]=='vertex': mn=min(mn,float(s[3]))
print(f'{mn:.3f}')")
  { echo 'PREVIEW_OFF=1;'; echo 'include <enclosure.scad>'; echo "add_brim(w=2, minz=$MZ) $mod();"; } > .rb_$mod.scad
  openscad -o stl/brim/$mod.stl .rb_$mod.scad 2>&1 | grep -iE error
  rm -f .rb_$mod.scad
  python3 -c "
mn=1e9;mx=-1e9
for l in open('stl/brim/$mod.stl'):
 s=l.split()
 if len(s)>=4 and s[0]=='vertex': x=float(s[1]);mn=min(mn,x);mx=max(mx,x)
print('$mod brimmed = %.1f mm -> %s'%(mx-mn,'OK' if mx-mn<148 else 'TIGHT'))" >> /tmp/rebake.out
done
echo DONE >> /tmp/rebake.out

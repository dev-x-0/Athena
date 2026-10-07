export const campaigns=[
{id:'CMP001',name:'Summer Performance',platform:'Meta',spend:12400,revenue:43200,roas:3.48,conv:184,status:'Scale'},
{id:'CMP002',name:'High Margin Push',platform:'Google',spend:8100,revenue:31400,roas:3.88,conv:121,status:'Scale'},
{id:'CMP003',name:'Clearance Drive',platform:'TikTok',spend:8200,revenue:18600,roas:2.27,conv:73,status:'Watch'},
{id:'CMP004',name:'Retargeting',platform:'Meta',spend:6700,revenue:17200,roas:2.57,conv:68,status:'Hold'},
{id:'CMP006',name:'Low ROAS Test',platform:'Google',spend:15400,revenue:0,roas:0,conv:0,status:'Reduce'}];
export const products=[
['SKU001','Product 01','46.2%','84','₹4.2K','₹18.1K','3.48x','Healthy'],['SKU002','Product 02','7.9%','52','₹9.4K','₹12.0K','1.28x','Low margin'],['SKU003','Product 03','42.1%','0','₹8.2K','₹0','0x','Out of stock'],['SKU004','Product 04','51.8%','91','₹6.1K','₹23.7K','3.89x','Opportunity'],['SKU005','Product 05','38.4%','117','₹5.7K','₹16.4K','2.88x','Healthy']];
export const findings=[
{type:'critical',title:'SKU003 is being advertised while out of stock.',body:'Athena detected ad spend against a product with 0 available units.',metric:'₹8,240 spend · 0 units',action:'Pause or redirect spend'},
{type:'warning',title:'CMP006 is spending without conversions.',body:'The campaign has material spend but has recorded zero conversions.',metric:'₹15,400 spend · 0 conversions',action:'Reduce budget'},
{type:'opportunity',title:'SKU004 has strong economics and healthy inventory.',body:'High margin, healthy stock and strong ROAS make this a candidate for scale.',metric:'51.8% margin · 3.89x ROAS',action:'Review scale'},
{type:'observation',title:'SKU010 has sales without an advertising record.',body:'This may indicate organic demand or an attribution gap.',metric:'Sales detected · no ad record',action:'Investigate attribution'}];
export const trend=[{d:'Sep 15',spend:1200,revenue:3200},{d:'Sep 18',spend:1800,revenue:5100},{d:'Sep 21',spend:2100,revenue:6900},{d:'Sep 24',spend:2500,revenue:8200},{d:'Sep 27',spend:2800,revenue:9100},{d:'Sep 30',spend:3100,revenue:10500},{d:'Oct 03',spend:3500,revenue:12400},{d:'Oct 06',spend:3900,revenue:13800}];

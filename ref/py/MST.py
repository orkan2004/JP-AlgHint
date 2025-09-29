def kruskal_mst(n, edges):
    # edges: iterable of (u,v,w)
    parent=list(range(n)); rank=[0]*n
    def f(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def u(a,b):
        a=f(a); b=f(b)
        if a==b: return False
        if rank[a]<rank[b]: a,b=b,a
        parent[b]=a
        if rank[a]==rank[b]: rank[a]+=1
        return True
    total=0; used=[]
    for u_,v_,w in sorted(edges, key=lambda x:(x[2],x[0],x[1])):
        if u(u_,v_): total+=w; used.append((u_,v_,w))
    return total, used

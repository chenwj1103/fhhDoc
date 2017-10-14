IndexFilter

IndexFilter决定了查询优化器对于某一类型的查询将如何使用index，indexFilter仅影响查询优化器对于该类查询可以用尝试哪些index的执行计划分析，查询优化器还是根据分析情况选择最优计划。

如果某一类型的查询设定了IndexFilter，那么执行时通过hint指定了其他的index，查询优化器将会忽略hint所设置index，仍然使用indexfilter中设定的查询计划。

IndexFilter可以通过命令移除，也将在实例重启后清空。

IndexFilter的创建

可以通过如下命令为某一个collection建立indexFilter

db.runCommand(
   {
      planCacheSetFilter: <collection>,
      query: <query>,
      sort: <sort>,
      projection: <projection>,
      indexes: [ <index1>, <index2>, ...]
   }
)
db.runCommand(
   {
      planCacheSetFilter: "orders",
      query: { status: "A" },
      indexes: [
         { cust_id: 1, status: 1 },
         { status: 1, order_date: -1 }
      ]
   }
)
上图针对orders表建立了一个indexFilter，indexFilter指定了对于orders表只有status条件（仅对status进行查询，无sort等）的查询的indexes，故下图的查询语句的查询优化器仅仅会从{cust_id:1,status:1}和{status:1,order_date:-1}中进行winning plan的选择

db.orders.find( { status: "D" } )
db.orders.find( { status: "P" } )
indexFilter的列表

可以通过如下命令展示某一个collecton的所有indexFilter

db.runCommand( { planCacheListFilters: <collection> } )
indexFilter的删除

可以通过如下命令对IndexFilter进行删除

db.runCommand(
   {
      planCacheClearFilters: <collection>,
      query: <query pattern>,
      sort: <sort specification>,
      projection: <projection specification>
   }
)
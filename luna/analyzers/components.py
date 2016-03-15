#-------------------------------------
# Analyzers
#-------------------------------------

# TODO: handle also analyzers. The following is just an idea of a possible approach

# An Analyzer processes some data (Points or Regions/Slots) encapsulated in a Set(DataSet/Series/DataSeries/DataTimeSeries) and return a free-form result (dimensional/adimensional)

# An AnalyzerProcess run one or more analyzer and return a free-form result (dimensional/adimensional). If the results are defined in terms of slots, then it behaves like an AggregatorProcess, otherwise it just run a single analyzer.

class Analyzer(object):
    pass

class AnalyzerProcess(object):
    pass





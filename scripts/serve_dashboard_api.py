"""Serve the local read-only dashboard API and explicit investigation handoffs."""
from _bootstrap import ROOT
from dashboard.server import main
if __name__=='__main__': main()

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.accountmanagement.models import Organization, OrganizationSettings
from mangrove.datastore.database import get_db_manager
from  datawinners import settings

def get_database_manager(request):
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSettings.objects.get(organization = organization)
    db = organization_settings.document_store
    return get_db_manager(server=settings.COUCH_DB_SERVER, database=db)